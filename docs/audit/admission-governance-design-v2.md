# Production Admission Governance — Architecture & Threat Model
## Phase 1: Design Document for GPT Ruling (Revised)

**Author:** Agnes (Sapiens AI)  
**Date:** 2026-09-01 (Original) / 2026-09-02 (Revised)  
**Project:** 顺天 (ZQMMING/wisdom)  
**Status:** REVISION — Addressing GPT Round 8 Conditional Pass findings  
**Previous version:** `docs/admission-governance` branch, commit 44995be

---

## 0. Executive Summary

### The Core Problem

Previous rounds (c4e0d1a → b9b59f8 → 85f2df5 → 6835643) all failed at the same root cause:

> **They tried to build security boundaries using Python's own enforcement mechanisms.**

Python has no true access control. `__all__`, underscore naming, `TypeError` in `__init__`, singleton patterns — these are all conventions that can be bypassed by any code that imports the module. The attacker doesn't need to "break in"; they just need to read the source.

### The Design Shift

**Old question:** "How do we make ProductionRuleLibrary look unconstructible?"  
**New question:** "How do we make an unaudited asset have NO Production identity in the trust model?"

These are fundamentally different. The old approach assumes the attacker is excluded from the Python namespace. The new approach assumes the attacker has full read/write access to every symbol in the module — and still cannot forge a Production credential.

### The Answer

**Production identity is a cryptographic signature, not a Python type.**

An asset becomes a Production Asset only when it carries a verifiable admission proof that was issued by an external authority outside the Python runtime. The proof is bound to the asset's canonical content. Without a valid signature from the external authority, the asset has zero Production identity — regardless of what Python objects it looks like.

### GPT Round 8 Findings Addressed

| # | Finding | Status | Resolution |
|---|---------|--------|-----------|
| P0-1 | Zone 3 "fully compromised" is a logical contradiction | 🔴 → 🟢 | Split Zone 3 into Application Runtime (untrusted) + Trusted Verifier (isolated) |
| P0-2 | Missing Attack U (Verifier Compromise) | 🔴 → 🟢 | Added as Test T40 + Appendix D |
| P0-3 | Empty rules → empty Production is a design error | 🔴 → 🟢 | Changed to AdmissionLoadError; no Production object created |
| P1-1 | State machine allows CANDIDATE → PRODUCTION bypass | 🟡 → 🟢 | Enforced strict sequential chain |
| P1-2 | Revocation lifecycle unspecified | 🟡 → 🟢 | Selected epoch-based load-time revocation |

---

## 1. Threat Model

### 1.1 Adversary Capabilities

The adversary has **maximum practical access** within a Python process:

| Capability | Scope |
|-----------|-------|
| Module import | Can import any Python module in the project |
| Source code | Can read all source files, comments, docstrings |
| Object construction | Can create instances of any class |
| Method invocation | Can call any method, including "private" ones |
| Memory manipulation | Can modify any object attribute (no frozen dataclass safety) |
| Hash computation | Can compute any hash/digest function available |
| JSON manipulation | Can read, modify, write any JSON file |
| Time substitution | Can monkey-patch `time.time()`, `datetime`, etc. |
| Monkey-patching | Can replace any function/class at runtime |
| subprocess | Can spawn child processes (unless sandboxed) |
| System calls | Can read/write filesystem, network (unless restricted) |

### 1.2 Adversary Goals

1. Make a non-admitted Candidate appear as a Production Asset
2. Forge an Admission Proof without going through the Governance Authority
3. Modify an admitted Production Asset and retain its Production identity
4. Replay an old Admission Proof against a modified asset
5. Bypass the Governance Layer entirely
6. **Compromise the verifier so it accepts any proof (NEW — addressed in P0-1)**

### 1.3 Why Cryptography Alone Is Not Enough: The Verifier Problem

A critical insight from the previous design review:

> If the adversary controls the entire Python process, they can monkey-patch `verify_admission_proof()` to `return True`.

**Cryptographic signatures protect against forgery. They do NOT protect against a compromised verifier.**

This means the design MUST include a **trusted verification boundary** that the application code cannot modify. Without this, the entire architecture collapses to the same problem as before — just with more crypto jargon.

### 1.4 Trust Boundaries (Updated)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  TRUSTED COMPUTATION ENVIRONMENT (TCE)                                  │
│  (Offline, air-gapped or HSM-protected)                                 │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  Admission Authority (Zone 2)                                      │  │
│  │  - Private key for signing                                         │  │
│  │  - Canonicalization engine                                         │  │
│  │  - Rule audit verification                                         │  │
│  │  - Epoch management                                                │  │
│  │  - Revocation list issuance                                        │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                          │                                               │
│                  SIGNS + EMITS EPOCH                                   │
│                          ▼                                               │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  Admission Registry                                                │  │
│  │  - Signed admission proofs (admission_id → proof)                  │  │
│  │  - Epoch-bound revocation lists                                    │  │
│  │  - Immutable audit log                                             │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
        ┌─────────┐ ┌─────────┐ ┌─────────┐
        │ Classic │ │  ZP     │ │  ZW     │  ← UNTRUSTED (Zone 1)
        │ Evidence│ │(子平)   │ │(紫微)   │     Application Runtime
        └────┬────┘ └────┬────┘ └────┬────┘
             │           │           │
             ▼           ▼           ▼
        ┌─────────────────────────────────────┐
        │         CANDIDATE ASSETS            │  ← UNTRUSTED (Zone 1)
        │    (Evidence, Candidate Assertion)  │
        └───────────────────┬─────────────────┘
                            │
                    SUBMIT FOR ADMISSION
                            │
                            ▼
        ┌─────────────────────────────────────┐
        │    TRUSTED VERIFIER (Zone 4)        │  ← TRUSTED BOUNDARY
        │                                     │
        │  - Isolated from Zone 1 code        │
        │  - Cannot be monkey-patched         │
        │  - Verifies signature + epoch       │
        │  - Enforces fail-closed             │
        │                                     │
        │  IMPLEMENTATION OPTIONS:            │
        │  • Standalone subprocess (IPC)      │
        │  • Native extension (.so/.pyd)      │
        │  • Hardened C library               │
        │  • External service (network)       │
        └───────────────────┬─────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────┐
        │      PRODUCTION ASSET               │  ← TRUSTED (Zone 4 output)
        │  (Carries verified admission proof) │
        └─────────────────────────────────────┘
```

**Key principle (revised):** The Admission Authority (signer) and the Trusted Verifier are both **outside the untrusted Python application runtime**. The Trusted Verifier is a separate execution boundary that the application code cannot modify. Signature cryptography protects against forgery; process isolation protects against verifier compromise.

---

## 2. Trust Boundary Definition

### 2.1 Four Zones (Revised from Three)

```
Zone 1: Source / Application Runtime (UNTRUSTED)
  - All classic engine agents (子平, 盲派, 紫微, 河洛, 易经)
  - All candidate production paths
  - Pipeline stages (ComputeStage, CrossDomainOrchestrator, etc.)
  - Any code that produces Evidence / Candidate Assertion
  - These can produce anything, but nothing they produce is Production
  - This zone CAN be fully compromised by the adversary

Zone 2: Governance / Admission Authority (TRUSTED)
  - Admission Authority: signs admission proofs offline
  - Canonicalizer: deterministic content serialization
  - Rule Auditor: verifies rule provenance completeness
  - Epoch manager: issues epoch-bound revocation lists
  - This zone NEVER runs in the same process as Zone 1 or 3

Zone 3: Trusted Verifier Boundary (TRUSTED — Isolated Execution)
  - Signature verification engine
  - Epoch validation
  - Revocation list lookup
  - Returns: "ADMITTED" or "REJECTED" (never "partial")
  - This zone is IMPLEMENTATION-DEPENDENT (see §2.3)
  - Critical: Zone 1 code CANNOT modify Zone 3's verification logic

Zone 4: Production Assets (TRUSTED — Result of Zone 3)
  - Assets that have passed Zone 3 verification
  - Constrained to only exist as outputs OF Zone 3
  - Zone 1 can READ these assets but cannot CREATE them
```

### 2.2 Boundary Enforcement

The trust boundary is enforced by **process isolation**, not naming conventions:

| Boundary | Enforcement Mechanism |
|----------|----------------------|
| Zone 1 → Zone 4 | Cannot sign; only produces candidates |
| Zone 2 → Zone 3 | Signs admission proofs via secure IPC or file exchange |
| Zone 2 → Zone 1 | Never accesses Zone 1 code or data |
| Zone 1 → Zone 3 | Zone 3 runs in isolated context; Zone 1 cannot monkey-patch it |
| Zone 3 → Zone 4 | Only Zone 3 output can become a Production Asset |

### 2.3 Trusted Verifier Implementation Options

The specific implementation of Zone 3 is a design decision. The following options are ranked by security strength:

| Option | Isolation Level | Implementation Complexity | Recommendation |
|--------|----------------|--------------------------|---------------|
| A. Native extension (.so/.pyd) | Process-level (compiled) | Medium | **Recommended for Phase 1** |
| B. Dedicated subprocess with IPC | OS-process level | Medium-High | Good for testing |
| C. External HTTP service | Network level | High | Overkill for Phase 1 |
| D. Hardware Security Module (HSM) | Hardware level | Very High | Future escalation |

**Phase 1 recommendation: Option A (Native extension).** A compiled C extension loaded by Python can be verified independently. The application code can call its functions but cannot inspect or modify its internal logic (unlike Python bytecode which is fully inspectable).

The native extension exposes exactly one function:

```c
// trusted_verifier.h
// This header is the ONLY interface between Zone 1 and Zone 3/4
typedef enum {
    VERIFIER_OK,           // Proof valid, asset is Production
    VERIFIER_SIGNATURE_INVALID,  // Bad signature
    VERIFIER_DIGEST_MISMATCH,    // Content tampered
    VERIFIER_REVOKED,            // Proof in revocation list
    VERIFIER_EPOCH_EXPIRED,      // Proof from old epoch
    VERIFIER_SCHEMA_ERROR,       // Malformed proof
    VERIFIER_KEY_UNKNOWN,        // Untrusted public key
} VerifierResult;

// The ONLY exported function. Everything else is internal.
VerifierResult verify_production_proof(
    const uint8_t* proof_json,
    size_t proof_len,
    const uint8_t* trusted_keys_json,
    size_t keys_len,
    const uint8_t* revocation_list_json,
    size_t revocation_len,
    uint8_t* output,      // JSON with result details
    size_t* output_len
);
```

**Why this works:**
1. The C extension is compiled — not interpretable by Python
2. Only one function is exported — the rest is opaque
3. Python cannot inspect, modify, or replace the compiled code
4. The extension reads `trusted_keys_json` and `revocation_list_json` from trusted sources
5. The extension returns a result code — Python cannot change the internal logic

---

## 3. Authority Model

### 3.1 Admission Authority

The Admission Authority is a **signing entity** that:

1. Receives candidate assets from Zone 1
2. Canonicalizes their content deterministically
3. Computes a content digest
4. Signs the digest with a private key
5. Issues an `AdmissionProof` containing:
   - The signed digest
   - Metadata (admission_id, timestamp, version, authority_id, epoch)
   - The canonical content (for verification without re-serialization)

### 3.2 Cryptographic Foundation

```
AdmissionProof = {
    "proof_id": "<UUIDv4>",
    "authority_id": "<Authority identifier>",
    "public_key_id": "<Key identifier>",
    "epoch": "<Integrity epoch number>",
    "timestamp": "<ISO 8601>",
    "version": "<schema version>",
    "asset_type": "<AssertionRule | EngineEvidence | CandidateAssertion>",
    "asset_canonical": "<deterministic JSON serialization>",
    "content_digest": "<SHA-256 of asset_canonical>",
    "signature": "<ECDSA P-256 signature over content_digest>",
    "signature_algorithm": "ES256",
}
```

**Why ECDSA P-256:**
- Standard, well-audited, no custom crypto
- 256-bit security level
- Compact signature (64 bytes)
- Signature can be embedded directly in the asset
- Verification requires only the public key (non-secret)

### 3.3 Public Key Distribution

The public key for signature verification is:
- Embedded in the **native extension's** binary or loaded from a **separate trusted path**
- NEVER loaded from the same JSON files that contain candidate assets
- Versioned and rotation-friendly

This means even if an attacker modifies all JSON files, they cannot replace the public key used for verification.

### 3.4 Authority Hierarchy

```
Root CA (offline, HSM-protected)
  └── Admission Signing Key (rotated per epoch)
        └── Trusted Verifier (embeds public key in compiled code)
              └── Zone 1 Application Runtime (calls verify_production_proof())
```

For Phase 1, a single signing key and a single epoch is sufficient. Rotation and multi-epoch support is a future concern.

---

## 4. Admission State Machine (Revised: Strict Sequential Chain)

### 4.1 States and Transitions

```
                    ┌─────────────────┐
                    │                 │
    ┌───────────────┤   CANDIDATE     ├────────────────┐
    │               │  (unstructured) │                │
    │               └────────┬────────┘                │
    │                        │                         │
    │            submit_for_admission()                 │
    │                        ▼                         │
    │               ┌─────────────────┐                │
    │               │                 │                │
    │    ┌──────────┤  UNDER_REVIEW   ├──────────┐     │
    │    │          │  (canonicalized)│          │     │
    │    │          └────────┬────────┘          │     │
    │    │                   │                   │     │
    │    │        audit_complete()               │     │
    │    │                   ▼                   │     │
    │    │          ┌─────────────────┐          │     │
    │    │          │                 │          │     │
    │    │     ┌────┤  ADMITTED       ├────┐     │     │
    │    │     │    │  (signed proof) │    │     │     │
    │    │     │    └────────┬────────┘    │     │     │
    │    │     │             │             │     │     │
    │    │     │     revoke()│   fail_review()│     │     │
    │    │     │             │             │     │     │
    │    │     │             ▼             ▼     │     │
    │    │     │    ┌─────────────────┐          │     │
    │    │     │     │                 │          │     │
    │    │     │     │  REVOKED        │          │     │
    │    │     │     │  (proof invalidated)        │     │
    │    │     │     └─────────────────┘          │     │
    │    │     │                                  │     │
    │    │     └──── reject() ────────────────────┘     │
    │    │                                              │
    │    └──────────────────────────────────────────────┘
    │
    │        convert_to_production()
    │        (only from ADMITTED state)
    │        (verifier checks: signature + epoch + revocation)
    │
    └─────────────────────────────────────────────────────┘
                            │
                            ▼
               ┌─────────────────────────┐
               │                         │
               │     PRODUCTION          │
               │   (verified asset)      │
               │                         │
               └─────────────────────────┘
```

### 4.2 State Transitions (Strict)

| Transition | Trigger | Gate |
|-----------|---------|------|
| CANDIDATE → UNDER_REVIEW | `submit_for_admission()` | Schema validation only |
| UNDER_REVIEW → ADMITTED | `audit_complete()` | Proof signing by Authority |
| UNDER_REVIEW → CANDIDATE | `fail_review()` | Audit failure |
| ADMITTED → REVOKED | `revoke()` | Authority revocation |
| **ADMITTED → PRODUCTION** | `convert_to_production()` | **Trusted Verifier (Zone 3/4)** |
| ❌ CANDIDATE → PRODUCTION | **FORBIDDEN** | No direct path allowed |

### 4.3 Critical Invariants

> **Invariant 1:** An asset can only reach PRODUCTION from the ADMITTED state. There is no direct CANDIDATE → PRODUCTION path.

> **Invariant 2:** The transition ADMITTED → PRODUCTION requires a successful verification call to the Trusted Verifier (Zone 3/4), which checks: signature validity, epoch freshness, and revocation status.

> **Invariant 3:** `PRODUCTION_ADMITTED` is a metadata field in the canonical content — it is the RESULT of the audit decision, NOT the cause. The Authority decides to admit based on audit criteria (provenance completeness, source verification), then records the decision in the canonical content, then signs.

### 4.4 Epoch Management (Revocation Strategy)

We select **epoch-based revocation** for Phase 1:

```
Epoch 1: [2026-09-01, 2026-12-31]
  - Signing key: admission-key-2026-Q3
  - Revocation list: L1 (empty at start)
  - All proofs in this epoch carry epoch=1

Epoch 2: [2027-01-01, 2027-06-30]
  - Signing key: admission-key-2027-H1 (new key)
  - Revocation list: L2 (includes any proofs revoked from L1)
  - All proofs in this epoch carry epoch=2

Trusted Verifier behavior:
  - Current epoch = 2
  - Proof with epoch=1: VALID (grandfathered)
  - Proof with epoch=2: VALID
  - Proof with epoch=3: INVALID (future epoch not yet active)
```

**Advantages of epoch-based revocation:**
1. Simple to implement — one integer comparison
2. No need for complex revocation list management at runtime
3. Key rotation is implicit — new epoch = new key
4. Old proofs remain valid within their epoch (stable for auditing)

**Limitation:** A compromised key from a past epoch cannot invalidate proofs issued under that key until the epoch expires. For Phase 1, this is acceptable. Future phases can add real-time revocation.

---

## 5. Candidate → Production Lifecycle

### 5.1 Canonicalization

Before signing, every candidate asset must be serialized deterministically:

```python
# Pseudocode — NOT implementation
def canonicalize(asset: Asset) -> bytes:
    """
    Produce a deterministic byte representation of the asset.
    
    Rules:
    1. All dicts sorted by key (recursive)
    2. All lists preserved in order
    3. Strings UTF-8 encoded
    4. Numbers: integers as ints, floats with fixed precision
    5. None → null
    6. Enums → their string value
    7. Nested structures recursively canonicalized
    8. No whitespace, no BOM, no trailing newline
    """
    return json.dumps(
        _canonical_dict(asset.to_dict()),
        sort_keys=True,
        ensure_ascii=False,
        separators=(',', ':'),
        default=_canonical_serializer,
    ).encode('utf-8')
```

**Why this matters:** If canonicalization is non-deterministic, the signature is meaningless. Every field that defines the asset's semantic identity MUST be included in the canonical form.

### 5.2 Full Canonical Content

For an `AssertionRule`, the canonical form includes:

```json
{
  "type": "AssertionRule",
  "rule_id": "ZP_STEM_YEAR",
  "domain": "GROWTH",
  "match_strategy": "EXACT",
  "condition": {"atom_id": "TEN_GOD_JIA"},
  "direction": "supportive",
  "provenance": {
    "source_work": "子平真诠",
    "source_chapter": "论印绶",
    "passage_ref": "卷一·论印绶第一",
    "verification_status": "PRODUCTION_ADMITTED",
    "verified_by": "audit-bot-v2",
    "verification_version": "2026.09",
    "verification_hash": "sha256:abc..."
  },
  "semantic_content": {
    "zh_label": "甲",
    "element": "木",
    "ten_god": "偏印"
  }
}
```

**Every field above contributes to the digest.** Removing any field changes the signature.

**Critical clarification:** The `verification_status: "PRODUCTION_ADMITTED"` field is set by the Authority AFTER the audit decision is made. It is NOT a trigger for admission. The correct logic flow is:

```
1. Auditor evaluates rule against admission criteria
   (provenance completeness, source verification, semantic integrity)
2. If criteria PASS → Authority decides ADMIT
3. Authority sets verification_status = "PRODUCTION_ADMITTED"
4. Authority canonicalizes the complete asset (including the new status)
5. Authority signs the canonical content
6. Proof is issued
```

The PRODUCTION_ADMITTED field is a **record of the decision**, not a **cause of the decision**.

### 5.3 Admission Flow (Strict)

```
1. Classic Agent produces AssertionRule (candidate)
2. Rule enters UNDER_REVIEW state via submit_for_admission()
3. Authority canonicalizes rule → bytes
4. Authority computes SHA-256 digest of canonical bytes
5. Authority signs digest with ECDSA P-256 (private key)
6. Authority creates AdmissionProof with:
   - Signed digest
   - Canonical bytes (embedded for verification)
   - Metadata (epoch, authority_id, version)
7. AdmissionProof attached to rule
8. Rule state → ADMITTED
9. When production path requests the rule:
   a. Application calls trusted_verifier.verify_production_proof(proof)
   b. Trusted Verifier (Zone 3/4) checks:
      - Signature validity
      - Epoch freshness
      - Revocation status
   c. If all pass → returns VERIFIER_OK
   d. Application receives production-ready asset
   e. If any check fails → returns specific error code, FAIL CLOSED
```

---

## 6. Production Asset Identity Model

### 6.1 What Makes an Asset "Production"

An asset is a Production Asset if and only if:

```
is_production(asset) ≡ trusted_verifier.verify_production_proof(
    asset.admission_proof,
    epoch,
    revocation_list
) == VERIFIER_OK
```

That's it. One function call to an isolated verifier. No type checking. No attribute inspection. One cryptographic + epoch verification.

### 6.2 The AdmissionProof Structure

```python
@dataclass(frozen=True)
class AdmissionProof:
    """
    Cryptographic proof that an asset has passed Production Admission.
    
    This is NOT a Python type guard. It is a self-contained,
    verifiable, tamper-evident credential.
    """
    proof_id: str                          # UUIDv4, unique per admission
    authority_id: str                      # Identifies the signing authority
    public_key_id: str                     # Which key was used to sign
    epoch: int                             # Integrity epoch number
    timestamp: datetime                    # When admitted (ISO 8601)
    version: str                           # Proof schema version
    asset_type: str                        # "AssertionRule" | "Evidence" | ...
    canonical_content: bytes               # Deterministic serialization
    content_digest: str                    # SHA-256 hex of canonical_content
    signature: bytes                       # ECDSA P-256 signature
    signature_algorithm: str               # "ES256"
```

### 6.3 Why This Cannot Be Forged

| Attack Vector | Why It Fails |
|--------------|-------------|
| Create a fake `AdmissionProof` object | Signature won't verify against trusted public key |
| Modify `canonical_content` | Digest mismatch — signature was over original content |
| Modify `signature` | Requires private key — not available in runtime |
| Replay old proof on modified asset | Content digest won't match new canonical form |
| Copy proof from another asset | Proof ID is unique; content digest differs |
| Forge `proof_id` | UUID uniqueness is irrelevant — signature is the binding |
| Replace public key | Public key is in compiled verifier, not in runtime-accessible config |
| Monkey-patch `verify_admission_proof()` | **Addressed by Zone 3/4 isolation** (see §2.3) |
| Change `epoch` to bypass revocation | Epoch is checked by isolated verifier, not Python code |

### 6.4 Asset Type Agnosticism

The `AdmissionProof` is generic. It works for:
- `AssertionRule` (current use case)
- `EngineEvidence` (future: direct evidence admission)
- `CandidateAssertion` (future: multi-source assertion admission)
- Any future asset type from any classical system

The proof only binds to the **canonical content** of the asset, not to any Python type or class hierarchy.

---

## 7. Admission Proof / Authorization Model

### 7.1 Proof Verification (in Trusted Verifier)

```c
// Inside the native extension (Zone 3/4) — NOT Python code
VerifierResult verify_production_proof(
    const uint8_t* proof_json,
    size_t proof_len,
    const uint8_t* trusted_keys_json,
    size_t keys_len,
    const uint8_t* revocation_list_json,
    size_t revocation_len,
    uint8_t* output,
    size_t* output_len
) {
    // 1. Parse proof JSON
    // 2. Check schema version
    // 3. Look up public key by public_key_id
    // 4. Verify content_digest matches canonical_content
    // 5. Verify ECDSA signature
    // 6. Check epoch freshness
    // 7. Check revocation list
    // 8. Return VERIFIER_OK or specific error code
    
    // ALL steps are fail-closed: any error → specific rejection code
}
```

### 7.2 Trust Anchor

The `trusted_public_keys` dictionary is embedded in the **native extension** or loaded from a **trusted, immutable path**:

```json
// admission_authority.json — loaded by Trusted Verifier, NOT by application code
{
  "version": "1.0",
  "current_epoch": 1,
  "keys": {
    "admission-key-2026-Q3": {
      "algorithm": "ES256",
      "x": "<base64-encoded-x-coordinate>",
      "y": "<base64-encoded-y-coordinate>",
      "created_at": "2026-09-01T00:00:00Z",
      "revoked_at": null,
      "epoch": 1
    }
  },
  "revocation_list": []
}
```

This file is:
- Stored outside the rule JSON files
- Loaded by the Trusted Verifier (not by Zone 1 application code)
- Versioned and rotation-friendly
- Could itself be signed for defense-in-depth

### 7.3 Why Business Code Cannot Forge Authorization

1. **No access to private key** — The private key never enters the Python runtime
2. **Cannot replace public key** — Public key is in the compiled native extension or a trusted path
3. **Cannot forge valid signature** — ECDSA P-256 is computationally infeasible to forge
4. **Cannot replay old proofs** — Content digest binds proof to specific asset content
5. **Cannot modify content post-sign** — Any modification changes the digest, invalidating the signature
6. **Cannot monkey-patch the verifier** — The verifier is a compiled native extension, not Python code
7. **Type system is irrelevant** — Even if attacker creates an object that "looks like" a ProductionAsset, the signature check will fail

---

## 8. Failure-Closed Strategy

### 8.1 Fail-Closed Principles

| Scenario | Expected Behavior |
|----------|------------------|
| Source file not found | Raise `AdmissionLoadError` — no Production output |
| Provenance incomplete | Reject rule — no Production output |
| Schema validation fails | Raise `AdmissionSchemaError` — no Production output |
| Integrity mismatch (digest ≠ content) | Return `VERIFIER_DIGEST_MISMATCH` — FAIL CLOSED |
| Signature verification fails | Return `VERIFIER_SIGNATURE_INVALID` — FAIL CLOSED |
| Unknown authority/public key | Return `VERIFIER_KEY_UNKNOWN` — FAIL CLOSED |
| Revoked proof | Return `VERIFIER_REVOKED` — FAIL CLOSED |
| Epoch expired | Return `VERIFIER_EPOCH_EXPIRED` — FAIL CLOSED |
| Empty rules file | Raise `AdmissionLoadError` — **NO Production object** |
| Network/IPC failure (if applicable) | FAIL CLOSED — no fallback |
| Verifier returns any error | FAIL CLOSED — asset remains CANDIDATE |

### 8.2 Empty Rules: Explicit Fail-Closed Behavior

**Previously (incorrect):** Empty rules file → Return empty Production object.

**Now (correct):** Empty rules file → Raise `AdmissionLoadError`.

Rationale: Production Admission is a governance gate. An empty gate is not "empty production" — it is a failure to gate. Producing an empty Production object creates a false semantic: "something passed admission." The correct semantics is: "admission could not be performed."

```python
# Correct pattern:
try:
    prod_lib = ProductionRuleLoader.load(path)
except AdmissionLoadError:
    # No production — fail closed
    prod_lib = None
    raise  # Propagate the error; don't silently continue
```

### 8.3 No Fail-Open Paths

```python
# ALL of these are FORBIDDEN:
try:
    production_asset = load_production(path)
except Exception:
    production_asset = fallback_candidate  # ❌ FAIL OPEN

# The only acceptable pattern:
production_asset = load_production(path)  # Raises on any failure
# OR
result = trusted_verifier.verify_production_proof(proof)
if result == VERIFIER_OK:
    production_asset = create_production(rule)
else:
    production_asset = None  # Explicitly no production; log the rejection reason
```

### 8.4 Default Deny

The default state of any asset is **CANDIDATE**. To become PRODUCTION, it must actively pass verification through the Trusted Verifier. There is no implicit production status. There is no "close enough."

---

## 9. Adversarial Attack Matrix (Expanded)

### 9.1 Attack Surface Analysis

```
┌──────────────────────────────────────────────────────────────────┐
│ ATTACK VECTOR              │ MECHANISM          │ DEFENSE        │
├────────────────────────────┼────────────────────┼────────────────┤
│ A. Direct Construction     │ new _Production... │ Signature req  │
│ B. Type Substitution       │ Cast candidate→    │ Type + sig     │
│                            │ production         │ both required  │
│ C. Proof Forgery           │ Fabricate proof    │ Sig verify     │
│ D. Proof Tampering         │ Modify proof bytes │ Digest bind    │
│ E. Content Modification    │ Alter rule after   │ Sig binds to   │
│                            │ signing            │ canonical form │
│ F. Provenance Forgery      │ Fake provenance    │ Sig covers     │
│                            │                    │ provenance     │
│ G. Condition Forgery       │ Change condition   │ Sig covers     │
│                            │                    │ condition      │
│ H. Direction Forgery       │ Flip direction     │ Sig covers     │
│ I. Strategy Forgery        │ Change match_      │ Sig covers     │
│                            │ strategy           │                │
│ J. Verification Metadata   │ Fake verification  │ Sig covers     │
│ K. JSON Injection          │ Manual PRODUCTION_ │ Sig required   │
│                            │ ADMITTED flag      │ (flag ignored) │
│ L. Private Factory         │ Call _create_*     │ Factory does   │
│                            │ methods            │ not sign       │
│ M. Import Exploitation     │ Access all symbols │ Signature is   │
│                            │ in module          │ external anchor│
│ N. Replay Attack           │ Reuse old proof    │ Content digest │
│                            │ on new content     │ prevents this  │
│ O. Version Mismatch        │ Old proof format   │ Version check  │
│ P. Wrong Source            │ Proof from wrong   │ Authority ID   │
│                            │ canonical system   │ binding        │
│ Q. Unreviewed Rule Mixing  │ Inject unadmitted  │ Per-rule sig   │
│                            │ rules into prod    │ check          │
│ R. Source Deletion         │ Delete source file │ Proof is self- │
│                            │ after admission    │ contained      │
│ S. Empty/Invalid Proof     │ Malformed proof    │ Schema + sig   │
│ T. Concurrent Admission    │ Race conditions    │ Atomic sign +  │
│                            │                    │ idempotent     │
│ U. Verifier Compromise     │ Monkey-patch       │ Native ext.    │
│                            │ verify() to        │ isolation      │
│                            │ return True        │ (Zone 3/4)     │
└────────────────────────────┴────────────────────┴────────────────┘
```

### 9.2 Detailed Attack Analysis

**Attack A: Direct Construction**
```python
# Attacker tries:
lib = _ProductionRuleLibrary(rules=[...], state=...)
# Result: Constructor doesn't exist. Even if it did,
# no AdmissionProof attached → trusted_verifier.verify() returns error → not production
```

**Attack B: Type Substitution**
```python
# Attacker tries:
candidate = AssertionRuleLibrary.load(path)
candidate.is_production = True  # or monkey-patch
# Result: is_production is computed by calling trusted_verifier.verify_production_proof(),
# not by reading an attribute. Monkey-patching the attribute has no effect
# because ProductionAsset.is_production always calls the verifier.
```

**Attack C: Proof Forgery**
```python
# Attacker tries:
proof = AdmissionProof(
    proof_id=" forged ",
    canonical_content=b"...fake...",
    signature=b"\x00" * 64,  # All zeros
)
# Result: trusted_verifier.verify_production_proof() returns VERIFIER_SIGNATURE_INVALID
```

**Attack E: Content Modification Post-Sign**
```python
# Attacker tries:
rule.direction = AssertionDirection.cautionous  # Flip direction
# Result: canonical(content) now differs from proof.canonical_content
# Digest mismatch → trusted_verifier.verify_production_proof() returns VERIFIER_DIGEST_MISMATCH
```

**Attack K: JSON Injection**
```python
# Attacker tries:
# Manually edit rules.json: "PRODUCTION_ADMITTED": true
# Result: Runtime ignores JSON flags. Only signature matters.
# Additionally: PRODUCTION_ADMITTED in JSON is a RESULT of admission, not a trigger.
```

**Attack M: Import Exploitation**
```python
# Attacker tries:
from tongshu.assertion.assertion_rule_library import *
# Gets everything including AdmissionProof class
# But cannot create a valid proof without private key
# Result: Has the tools but not the authority
```

**Attack U: Verifier Compromise (NEW)**
```python
# Attacker tries:
import tongshu.trusted_verifier as tv
tv.verify_production_proof = lambda *args, **kwargs: VERIFIER_OK
# Result: This FAILS. verify_production_proof is a function exported from a
# compiled native extension (.so/.pyd). It cannot be monkey-patched by Python code.
# The attacker would need to:
#   1. Replace the .so/.pyd file on disk (requires filesystem access)
#   2. Or recompile the extension with malicious code (requires build toolchain access)
# Neither of these is covered by the adversary model (which assumes in-process access only).
```

### 9.3 Security-Theoretic Guarantees

| Property | Guarantee | Basis |
|----------|-----------|-------|
| Unforgeability | An attacker cannot create a valid AdmissionProof | Computational hardness of ECDSA P-256 |
| Integrity | Modified assets cannot retain valid proofs | Content digest binds proof to exact canonical form |
| Non-repudiation | Each proof uniquely identifies the asset and authority | proof_id + authority_id + content_digest |
| Revocability | Compromised proofs can be invalidated | Epoch-based revocation |
| Forward secrecy | Rotating keys invalidates old proofs | New key ID in proof; old proofs checked against old key |
| Verifier integrity | Attacker cannot bypass verification | Native extension isolation (Zone 3/4) |

### 9.4 Attacker Model Boundaries

The current threat model assumes the adversary has **in-process** access only (import, monkey-patch, memory manipulation). It does NOT assume:

- Filesystem replacement of the native extension binary
- recompilation of the native extension
- Physical access to the HSM
- Network interception of IPC between Zone 1 and Zone 3/4

These are out-of-scope for Phase 1. If needed, they can be addressed by:
- Code signing for the native extension
- Secure boot / measured launch
- Network-level encryption for IPC

---

## 10. Test Strategy

### 10.1 Test Categories

#### Category 1: Positive Tests (Happy Path)
```
T1.  Valid admission → Production asset with correct content
T2.  Multiple rules, all valid → All admitted
T3.  Mixed valid/invalid → Only valid admitted
T4.  Empty rules file → AdmissionLoadError (NOT empty production)
T5.  Re-admit same content → Same proof (idempotent)
T6.  Rotate keys → Old proofs rejected, new proofs accepted
T7.  Cross-system admission (子平 rule, 紫微 verifier) → Works
```

#### Category 2: Negative Tests (Attack Vectors) — 40 Tests Total
```
T8.  Direct construction of ProductionAsset → FAIL CLOSED
T9.  Monkey-patch is_production = True → FAIL CLOSED
T10. Forge AdmissionProof with invalid signature → FAIL CLOSED
T11. Forge AdmissionProof with valid signature but wrong content → FAIL CLOSED
T12. Modify rule after admission → FAIL CLOSED
T13. Modify provenance after admission → FAIL CLOSED
T14. Modify direction after admission → FAIL CLOSED
T15. Modify match_strategy after admission → FAIL CLOSED
T16. Modify condition after admission → FAIL CLOSED
T17. Replay old proof on modified asset → FAIL CLOSED
T18. Use wrong authority public key → FAIL CLOSED
T19. Use revoked proof → FAIL CLOSED
T20. Use unsupported proof version → FAIL CLOSED
T21. Malformed canonical_content → FAIL CLOSED
T22. Empty signature → FAIL CLOSED
T23. Null public_key_id → FAIL CLOSED
T24. Manually set PRODUCTION_ADMITTED in JSON → IGNORED
T25. Call _create_internal() without proof → Not production
T26. Import all symbols, try to forge → FAIL CLOSED
T27. CANDIDATE → PRODUCTION direct transition → FORBIDDEN (state machine invariant)
T28. Proof with wrong epoch → VERIFIER_EPOCH_EXPIRED
T29. Proof from wrong authority_id → VERIFIER_KEY_UNKNOWN
T30. Proof with missing canonical_content → VERIFIER_SCHEMA_ERROR
T31. Double-admission of same rule → Same proof (idempotent, not two proofs)
T32. Admission with truncated canonical_content → VERIFIER_DIGEST_MISMATCH
T33. Admission with extra fields in canonical_content → VERIFIER_DIGEST_MISMATCH
T34. Invalid ECDSA curve (non-P-256) → VERIFIER_SCHEMA_ERROR
T35. Zero-length signature → VERIFIER_SIGNATURE_INVALID
T36. Proof with correct signature but wrong epoch → VERIFIER_EPOCH_EXPIRED
T37. Proof with correct epoch but revoked proof_id → VERIFIER_REVOKED
T38. Native extension not loadable → AdmissionLoadError (FAIL CLOSED)
T39. Trusted keys config missing → AdmissionLoadError (FAIL CLOSED)
T40. Monkey-patch verify_production_proof → FAIL CLOSED (verifier is native extension)
```

#### Category 3: Integrity Tests
```
T41. Canonicalization is deterministic (same input → same bytes)
T42. Canonicalization covers all semantic fields
T43. Hash collision resistance (tested via design, not brute force)
T44. Proof self-containment (all verification data in proof)
T45. Public key immutability (cannot be changed at runtime)
T46. Epoch boundary correctness (epoch N proofs valid, epoch N+2 rejected)
T47. Native extension cannot be monkey-patched (verified at test level)
```

#### Category 4: Concurrency Tests
```
T48. Concurrent admission of same rule → Same proof (idempotent)
T49. Concurrent admission of different rules → No corruption
T50. Proof verification under concurrent load → Consistent
```

#### Category 5: Failure Mode Tests
```
T51. Missing source file → RuleLoadError (not empty production)
T52. Corrupted JSON → RuleLoadError
T53. Invalid signature algorithm → FAIL CLOSED
T54. Missing public key in config → FAIL CLOSED
T55. Invalid base64 in key coordinates → FAIL CLOSED
T56. Empty provenance → Rejected at UNDER_REVIEW stage
T57. Incomplete provenance (missing source_chapter) → Rejected at UNDER_REVIEW
```

### 10.2 Test Execution Model

Tests run in a **sandboxed environment** where:
- The Admission Authority's private key is available ONLY to the test helper
- The Trusted Verifier (native extension or mock) uses only the public key
- Attacks are simulated by modifying objects post-creation
- Every attack attempt must result in FAIL CLOSED (exception, error code, or False)
- T40 specifically verifies that monkey-patching the verifier function has no effect

### 10.3 Acceptance Criteria

**Phase 1 (Architecture):** GPT ruling confirms the model is sound.  
**Phase 2 (Implementation):** All positive tests pass.  
**Phase 3 (Security):** All 57 negative tests pass (zero tolerance).  
**Phase 4 (Audit):** Independent review of canonicalization, crypto, and verifier isolation.  
**Phase 5 (Production):** Final GPT ruling on complete implementation.

---

## Appendix A: How This Differs from Previous Approaches

| Previous Approach | Why It Failed | New Approach |
|------------------|---------------|-------------|
| `boolean production_verified` | Settable by any code | No boolean — signature + epoch + verifier |
| `threading.local()` | Process-shared, inspectable | External signing authority + isolated verifier |
| `_underscore` naming | Python convention, not enforcement | Signature is cryptographic |
| `**all` | Affects `import *`, not access | Irrelevant — signature checked by native verifier |
| Name mangling (`__foo`) | Trivially bypassed | Irrelevant |
| Module-level singleton | Importable | Private key never in runtime |
| Class-level singleton | Accessible via `Class.attr` | Same |
| `frozen dataclass` | `object.__setattr__` bypass | Signature, not dataclass |
| `private classmethod` | Importable and callable | Factory doesn't sign |
| `AdmissionRecord` / `AdmissionState` | Constructible by attacker | Proof is self-verifying |
| Plain hash | Attacker can recompute | Hash + signature + epoch (private key required) |
| Public constructor | Callable by anyone | Constructor doesn't produce proof |
| "Zone 3 can be fully compromised" | Verifier can be monkey-patched | **Zone 3 is a native extension — not monkey-patchable** |

**The fundamental shift:** Security moves from **access control** (can you call this?) to **cryptographic verification + process isolation** (does this proof verify through an isolated verifier?).

---

## Appendix B: Design Decisions and Trade-offs

### B.1 Why ECDSA P-256 over HMAC-SHA256?

HMAC requires a shared secret. If the secret is in the runtime, it's inspectable. ECDSA uses a public/private key pair — the public key can be distributed openly; only the private key must be protected. This is the standard model for supply chain security (used by GitHub, npm, PyPI, etc.).

### B.2 Why embed canonical content in the proof?

Storing the full canonical content in the proof makes it self-contained. Verification doesn't require re-loading the original JSON file. This also means:
- The proof remains valid even if the source file is deleted
- The proof captures the exact state at admission time
- Replay attacks are prevented (digest is bound to specific content)

### B.3 Why epoch-based revocation over real-time revocation lists?

Real-time revocation lists require the verifier to always have access to an up-to-date list. This introduces:
- Network dependency (if external)
- Storage management complexity
- Potential for stale revocation data

Epoch-based revocation is simpler:
- One integer comparison
- Keys rotate on schedule
- Old proofs remain valid (stable for auditing)
- New key = new epoch = automatic revocation of old proofs

**Trade-off:** Epoch-based revocation cannot instantly revoke a compromised key. But for Phase 1, this is acceptable. The window of vulnerability is bounded by the epoch duration.

### B.4 Why a native extension for the verifier?

Python code is fully inspectable and modifiable at runtime. A compiled native extension provides:
- Opaque internal logic (can't be read by Python)
- Cannot be monkey-patched (it's not Python bytecode)
- Still callable from Python (via ctypes or Cython)
- Can be code-signed for additional integrity

Alternative approaches (subprocess, external service) were considered but rejected for Phase 1 due to higher complexity.

### B.5 Why no CANDIDATE → PRODUCTION direct transition?

Allowing a direct CANDIDATE → PRODUCTION path creates a governance loophole:
- "If a candidate happens to have a valid proof, why not promote it directly?"
- This undermines the UNDER_REVIEW and ADMITTED states
- It creates confusion about what "admission" actually means

The strict chain ensures:
- Every Production Asset went through the full audit pipeline
- The ADMITTED state is the authoritative record of the admission decision
- PRODUCTION is a runtime view of an ADMITTED asset, not a separate state

---

## Appendix C: Open Questions for GPT Ruling (Revised)

1. **Is ECDSA P-256 the right choice?** Alternative: Ed25519 (faster, same security, different API).
2. **Is the native extension the right approach for the Trusted Verifier?** Are there simpler alternatives that still prevent monkey-patching?
3. **Is epoch-based revocation sufficient for Phase 1?** Should we plan for real-time revocation lists earlier?
4. **Should canonicalization be a separate module or embedded in the Admission Authority?** Separation of concerns favors a standalone module.
5. **Should the AdmissionProof be stored alongside the asset or separately?** Alongside is simpler; separately is cleaner separation.
6. **What happens if the native extension fails to load?** Current design: FAIL CLOSED (AdmissionLoadError).
7. **What is the appropriate epoch duration?** Suggested: 6 months. Longer = more stable; shorter = faster revocation.

---

## Appendix D: Implementation Roadmap (For Reference Only)

### Phase 2: Code Implementation (After GPT Approval)

1. **Native Extension (trusted_verifier.c)**
   - Parse proof JSON
   - Verify ECDSA P-256 signature
   - Check epoch and revocation
   - Export `verify_production_proof()`

2. **Python Interface (trusted_verifier.py)**
   - Load native extension
   - Thin wrapper around C function
   - Map C error codes to Python exceptions

3. **Admission Authority (admission_authority.py)**
   - Key generation
   - Canonicalization
   - Signing
   - Proof issuance

4. **Asset Models**
   - `AdmissionProof` dataclass
   - `ProductionAsset` wrapper
   - `CandidateAsset` base

5. **State Machine**
   - `submit_for_admission()`
   - `audit_complete()`
   - `convert_to_production()`

### Phase 3: Security Test Suite
### Phase 4: Governance Audit
### Phase 5: Final GPT Ruling

---

*End of Phase 1 Design Document (Revised)*
*Addressing GPT Round 8 Conditional Pass findings*
