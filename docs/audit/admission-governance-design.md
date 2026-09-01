# Production Admission Governance — Architecture & Threat Model
## Phase 1: Design Document for GPT Ruling

**Author:** Agnes (Sapiens AI)  
**Date:** 2026-09-01  
**Project:** 顺天 (ZQMMING/wisdom)  
**Status:** DRAFT — Awaiting GPT Architecture Ruling  

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

### 1.3 Trust Boundaries

```
┌─────────────────────────────────────────────────────────────────┐
│  TRUSTED COMPUTATION ENVIRONMENT (TCE)                          │
│  (Offline, air-gapped or HSM-protected)                         │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Admission Authority                                      │  │
│  │  - Private key for signing                                │  │
│  │  - Canonicalization engine                                │  │
│  │  - Rule audit verification                                │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          │                                      │
│                  SIGNS (offline)                                │
│                          ▼                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Admission Registry                                       │  │
│  │  - Signed admission proofs (admission_id → proof)         │  │
│  │  - Immutable log                                          │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
        ┌─────────┐ ┌─────────┐ ┌─────────┐
        │ Classic │ │  ZP     │ │  ZW     │  ← UNTRUSTED
        │ Evidence│ │(子平)   │ │(紫微)   │     Runtime
        └────┬────┘ └────┬────┘ └────┬────┘
             │           │           │
             ▼           ▼           ▼
        ┌─────────────────────────────────────┐
        │         CANDIDATE ASSETS            │  ← UNTRUSTED
        │    (Evidence, Candidate Assertion)  │
        └───────────────────┬─────────────────┘
                            │
                    SUBMIT FOR ADMISSION
                            │
                            ▼
        ┌─────────────────────────────────────┐
        │     PRODUCTION ADMISSION GATE       │  ← TRUSTED RUNTIME BOUNDARY
        │  (Verifies signature, not type)     │
        └───────────────────┬─────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────┐
        │      PRODUCTION ASSET               │  ← TRUSTED
        │  (Carries verified admission proof) │
        └─────────────────────────────────────┘
```

**Key principle:** The Admission Authority (signer) and the Runtime Verifier are separate components. The signer operates in a trusted context; the verifier operates in an untrusted context but only validates signatures.

---

## 2. Trust Boundary Definition

### 2.1 Three Zones

```
Zone 1: Source Zone (UNTRUSTED)
  - All classic engine agents (子平, 盲派, 紫微, 河洛, 易经)
  - All candidate production paths
  - Any code that produces Evidence / Candidate Assertion
  - These can produce anything, but nothing they produce is Production

Zone 2: Governance Zone (TRUSTED — Signing Authority)
  - Admission Authority: signs admission proofs offline
  - Canonicalizer: deterministic content serialization
  - Rule Auditor: verifies rule provenance completeness
  - This zone NEVER runs in the same process as Zone 1 or 3

Zone 3: Runtime Zone (SEMI-TRUSTED — Verification Only)
  - Production Admission Gate: verifies signatures
  - CrossDomainOrchestrator: consumes Production Assets
  - Pipeline stages: consume Production Assets
  - This zone can be fully compromised — it only checks signatures
```

### 2.2 Boundary Enforcement

The trust boundary is enforced by **process isolation**, not naming conventions:

| Boundary | Enforcement Mechanism |
|----------|----------------------|
| Zone 1 → Zone 3 | Cannot sign; only produces candidates |
| Zone 2 → Zone 3 | Signs admission proofs via secure IPC or file-based exchange |
| Zone 2 → Zone 1 | Never accesses Zone 1 code or data |
| Within Zone 3 | Signature verification is the ONLY gate |

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
   - Metadata (admission_id, timestamp, version, authority_id)
   - The canonical content (for verification without re-serialization)

### 3.2 Cryptographic Foundation

```
AdmissionProof = {
    "proof_id": "<UUIDv4>",
    "authority_id": "<Authority identifier>",
    "authority_public_key_id": "<Key identifier>",
    "timestamp": "<ISO 8601>",
    "version": "<schema version>",
    "asset_type": "<rule | assertion | evidence>",
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
- Embedded in the runtime binary/config (immutable after deployment)
- OR loaded from a trusted, signed configuration file
- NOT loaded from the same JSON files that contain candidate assets

This means even if an attacker modifies all JSON files, they cannot replace the public key used for verification.

### 3.4 Authority Hierarchy

```
Root CA (offline, HSM-protected)
  └── Admission Signing Key (rotated periodically)
        └── Runtime Verifier (trusts this key)
```

For Phase 1, a single signing key is sufficient. Rotation is a future concern.

---

## 4. Admission State Machine

### 4.1 States

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
    └──────────────── convert_to_production() ──────────┘
                        (signature verified)
                            │
                            ▼
               ┌─────────────────────────┐
               │                         │
               │     PRODUCTION          │
               │   (verified asset)      │
               │                         │
               └─────────────────────────┘
```

### 4.2 State Transitions

| Transition | Trigger | Gate |
|-----------|---------|------|
| CANDIDATE → UNDER_REVIEW | `submit_for_admission()` | None (internal) |
| UNDER_REVIEW → ADMITTED | `audit_complete()` | Proof signing by Authority |
| UNDER_REVIEW → CANDIDATE | `fail_review()` | Audit failure |
| ADMITTED → REVOKED | `revoke()` | Authority revocation |
| CANDIDATE → PRODUCTION | `convert_to_production()` | **Signature verification** |
| ADMITTED → PRODUCTION | `convert_to_production()` | Signature verification (redundant) |

### 4.3 Critical Invariant

> **An asset is PRODUCTION if and only if it carries a verifiable AdmissionProof issued by the trusted Authority.**

There is no other path. No type check, no flag check, no convention check. The ONLY question is: "Does this signature verify against the trusted public key?"

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

### 5.3 Admission Flow

```
1. Classic Agent produces AssertionRule (candidate)
2. Rule enters UNDER_REVIEW state via submit_for_admission()
3. Authority canonicalizes rule → bytes
4. Authority computes SHA-256 digest of canonical bytes
5. Authority signs digest with ECDSA P-256 (private key)
6. Authority creates AdmissionProof with:
   - Signed digest
   - Canonical bytes (embedded for verification)
   - Metadata
7. AdmissionProof attached to rule
8. Rule state → ADMITTED
9. Runtime loads rule, verifies signature against trusted public key
10. If valid → PRODUCTION Asset
    If invalid → FAIL CLOSED (treated as CANDIDATE at best)
```

---

## 6. Production Asset Identity Model

### 6.1 What Makes an Asset "Production"

An asset is a Production Asset if and only if:

```
is_production(asset) ≡ verify_signature(
    asset.admission_proof,
    trusted_public_key
) == True
```

That's it. One boolean function. No type checking. No attribute inspection. One cryptographic verification.

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
| Replace public key | Public key is from trusted config, not from asset JSON |

### 6.4 Asset Type Agnosticism

The `AdmissionProof` is generic. It works for:
- `AssertionRule` (current use case)
- `EngineEvidence` (future: direct evidence admission)
- `CandidateAssertion` (future: multi-source assertion admission)
- Any future asset type from any classical system

The proof only binds to the **canonical content** of the asset, not to any Python type or class hierarchy.

---

## 7. Admission Proof / Authorization Model

### 7.1 Proof Verification

```python
def verify_admission_proof(
    proof: AdmissionProof,
    trusted_public_keys: Dict[str, PublicKey],
) -> bool:
    """
    Verify that the proof is valid and not revoked.
    
    Returns True if and only if:
    1. The public key exists in trusted_keys
    2. The signature is valid over content_digest
    3. The content_digest matches canonical_content
    4. The proof is not in the revocation list
    5. The proof version is supported
    
    FAIL CLOSED: Any failure returns False.
    """
    if proof.version not in SUPPORTED_VERSIONS:
        return False  # FAIL CLOSED
    
    pubkey = trusted_public_keys.get(proof.public_key_id)
    if pubkey is None:
        return False  # FAIL CLOSED
    
    # Verify digest matches content
    actual_digest = sha256(proof.canonical_content).hexdigest()
    if actual_digest != proof.content_digest:
        return False  # FAIL CLOSED
    
    # Verify signature
    if not pubkey.verify_es256(
        digest=bytes.fromhex(proof.content_digest),
        signature=proof.signature,
    ):
        return False  # FAIL CLOSED
    
    # Check revocation
    if proof.proof_id in REVOCATION_LIST:
        return False  # FAIL CLOSED
    
    return True
```

### 7.2 Trust Anchor

The `trusted_public_keys` dictionary is loaded from a **separate, immutable configuration source**:

```json
// admission_authority.json — loaded once at boot, never from rule files
{
  "version": "1.0",
  "keys": {
    "admission-key-2026-09": {
      "algorithm": "ES256",
      "x": "<base64-encoded-x-coordinate>",
      "y": "<base64-encoded-y-coordinate>",
      "created_at": "2026-09-01T00:00:00Z",
      "revoked_at": null
    }
  },
  "revocation_list": []
}
```

This file is:
- Stored outside the rule JSON files
- Loaded from a trusted path (not from candidate asset directories)
- Versioned and rotation-friendly
- Signed itself (optional, for defense-in-depth)

### 7.3 Why Business Code Cannot Forge Authorization

1. **No access to private key** — The private key never enters the Python runtime
2. **Cannot replace public key** — Public key comes from trusted config, not from assets
3. **Cannot forge valid signature** — ECDSA P-256 is computationally infeasible to forge
4. **Cannot replay old proofs** — Content digest binds proof to specific asset content
5. **Cannot modify content post-sign** — Any modification changes the digest, invalidating the signature
6. **Type system is irrelevant** — Even if attacker creates an object that "looks like" a ProductionAsset, the signature check will fail

---

## 8. Failure-Closed Strategy

### 8.1 Fail-Closed Principles

| Scenario | Expected Behavior |
|----------|------------------|
| Source file not found | Raise `AdmissionLoadError` — no Production output |
| Provenance incomplete | Reject rule — no Production output |
| Schema validation fails | Raise `AdmissionSchemaError` — no Production output |
| Integrity mismatch (digest ≠ content) | Reject as unadmitted — FAIL CLOSED |
| Signature verification fails | Reject as unadmitted — FAIL CLOSED |
| Unknown authority/public key | Reject — FAIL CLOSED |
| Revoked proof | Reject — FAIL CLOSED |
| Empty rules file | Return empty Production (not error) — acknowledged gap |
| Network/IPC failure (if applicable) | FAIL CLOSED — no fallback |

### 8.2 No Fail-Open Paths

```python
# ALL of these are FORBIDDEN:
try:
    production_asset = load_production(path)
except Exception:
    production_asset = fallback_candidate  # ❌ FAIL OPEN

# The only acceptable pattern:
production_asset = load_production(path)  # Raises on any failure
# OR
if verify_admission_proof(proof, trusted_keys):
    production_asset = create_production(rule)
else:
    production_asset = None  # Explicitly no production
```

### 8.3 Default Deny

The default state of any asset is **CANDIDATE**. To become PRODUCTION, it must actively pass verification. There is no implicit production status. There is no "close enough."

---

## 9. Adversarial Attack Matrix

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
└────────────────────────────┴────────────────────┴────────────────┘
```

### 9.2 Detailed Attack Analysis

**Attack A: Direct Construction**
```python
# Attacker tries:
lib = _ProductionRuleLibrary(rules=[...], state=...)
# Result: Constructor doesn't exist. Even if it did,
# no AdmissionProof attached → verify() returns False → not production
```

**Attack B: Type Substitution**
```python
# Attacker tries:
candidate = AssertionRuleLibrary.load(path)
candidate.is_production = True  # or monkey-patch
# Result: is_production is now a computed property based on
# signature verification, not a settable attribute
```

**Attack C: Proof Forgery**
```python
# Attacker tries:
proof = AdmissionProof(
    proof_id=" forged ",
    canonical_content=b"...fake...",
    signature=b"\x00" * 64,  # All zeros
)
# Result: pubkey.verify_es256() returns False
```

**Attack E: Content Modification Post-Sign**
```python
# Attacker tries:
rule.direction = AssertionDirection.cautionous  # Flip direction
# Result: canonical(content) now differs from proof.canonical_content
# Digest mismatch → verification fails
```

**Attack K: JSON Injection**
```python
# Attacker tries:
# Manually edit rules.json: "PRODUCTION_ADMITTED": true
# Result: Runtime ignores JSON flags. Only signature matters.
```

**Attack M: Import Exploitation**
```python
# Attacker tries:
from tongshu.assertion.assertion_rule_library import *
# Gets everything including AdmissionProof class
# But cannot create a valid proof without private key
# Result: Has the tools but not the authority
```

### 9.3 Security-Theoretic Guarantees

| Property | Guarantee | Basis |
|----------|-----------|-------|
| Unforgeability | An attacker cannot create a valid AdmissionProof | Computational hardness of ECDSA P-256 |
| Integrity | Modified assets cannot retain valid proofs | Content digest binds proof to exact canonical form |
| Non-repudiation | Each proof uniquely identifies the asset and authority | proof_id + authority_id + content_digest |
| Revocability | Compromised proofs can be invalidated | Revocation list checked during verification |
| Forward secrecy | Rotating keys invalidates old proofs | New key ID in proof; old proofs checked against old key |

---

## 10. Test Strategy

### 10.1 Test Categories

#### Category 1: Positive Tests (Happy Path)
```
T1.  Valid admission → Production asset with correct content
T2.  Multiple rules, all valid → All admitted
T3.  Mixed valid/invalid → Only valid admitted
T4.  Empty rules file → Empty production (graceful)
T5.  Re-admit same content → Same proof (idempotent)
T6.  Rotate keys → Old proofs rejected, new proofs accepted
T7.  Cross-system admission (子平 rule, 紫微 verifier) → Works
```

#### Category 2: Negative Tests (Attack Vectors)
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
```

#### Category 3: Integrity Tests
```
T27. Canonicalization is deterministic (same input → same bytes)
T28. Canonicalization covers all semantic fields
T29. Hash collision resistance (tested via design, not brute force)
T30. Proof self-containment (all verification data in proof)
T31. Public key immutability (cannot be changed at runtime)
```

#### Category 4: Concurrency Tests
```
T32. Concurrent admission of same rule → Same proof (idempotent)
T33. Concurrent admission of different rules → No corruption
T34. Proof verification under concurrent load → Consistent
```

#### Category 5: Failure Mode Tests
```
T35. Missing source file → RuleLoadError (not empty production)
T36. Corrupted JSON → RuleLoadError
T37. Invalid signature algorithm → FAIL CLOSED
T38. Missing public key in config → FAIL CLOSED
T39. Invalid base64 in key coordinates → FAIL CLOSED
```

### 10.2 Test Execution Model

Tests run in a **sandboxed Python process** where:
- The Admission Authority's private key is available ONLY to the test helper
- The runtime verifier uses only the public key
- Attacks are simulated by modifying objects post-creation
- Every attack attempt must result in FAIL CLOSED (exception or False return)

### 10.3 Acceptance Criteria

**Phase 1 (Architecture):** GPT ruling confirms the model is sound.  
**Phase 2 (Implementation):** All positive tests pass.  
**Phase 3 (Security):** All 39 negative tests pass (zero tolerance).  
**Phase 4 (Audit):** Independent review of canonicalization and crypto.  
**Phase 5 (Production):** Final GPT ruling on complete implementation.

---

## Appendix A: How This Differs from Previous Approaches

| Previous Approach | Why It Failed | New Approach |
|------------------|---------------|-------------|
| `boolean production_verified` | Settable by any code | No boolean — signature-based |
| `threading.local()` | Process-shared, inspectable | External signing authority |
| `_underscore` naming | Python convention, not enforcement | Signature is cryptographic |
| `**all` | Affects `import *`, not access | Irrelevant — signature checked |
| Name mangling (`__foo`) | Trivially bypassed | Irrelevant |
| Module-level singleton | Importable | Private key never in runtime |
| Class-level singleton | Accessible via `Class.attr` | Same |
| `frozen dataclass` | `object.__setattr__` bypass | Signature, not dataclass |
| `private classmethod` | Importable and callable | Factory doesn't sign |
| `AdmissionRecord` / `AdmissionState` | Constructible by attacker | Proof is self-verifying |
| Plain hash | Attacker can recompute | Hash + signature (private key required) |
| Public constructor | Callable by anyone | Constructor doesn't produce proof |

**The fundamental shift:** Security moves from **access control** (can you call this?) to **cryptographic verification** (does this proof verify?).

---

## Appendix B: Design Decisions and Trade-offs

### B.1 Why ECDSA P-256 over HMAC-SHA256?

HMAC requires a shared secret. If the secret is in the runtime, it's inspectable. ECDSA uses a public/private key pair — the public key can be distributed openly; only the private key must be protected. This is the standard model for supply chain security (used by GitHub, npm, PyPI, etc.).

### B.2 Why embed canonical content in the proof?

Storing the full canonical content in the proof makes it self-contained. Verification doesn't require re-loading the original JSON file. This also means:
- The proof remains valid even if the source file is deleted
- The proof captures the exact state at admission time
- Replay attacks are prevented (digest is bound to specific content)

### B.3 Why not use Python's `secrets` or `os.urandom` for proof IDs?

Proof IDs are UUIDs for uniqueness tracking. The security comes from the signature, not the ID. UUID collisions are astronomically unlikely and don't compromise security even if they occur.

### B.4 What about performance?

Signature verification is fast (~微秒级). One verification per asset access is negligible compared to pipeline processing. For high-throughput scenarios, verification can be cached with a short TTL.

### B.5 What about key rotation?

The `public_key_id` field allows multiple keys to coexist. Old proofs signed with retired keys continue to verify. New admissions use the active key. Revocation list handles compromised keys.

---

## Appendix C: Open Questions for GPT Ruling

1. **Is ECDSA P-256 the right choice?** Alternative: Ed25519 (faster, same security, different API).
2. **Should the public key be embedded in binary or loaded from config?** Config is more flexible; binary is more tamper-resistant.
3. **Do we need a revocation list in the runtime, or is key rotation sufficient?** Revocation is faster than full key rotation.
4. **Should canonicalization be a separate module or embedded in the Admission Authority?** Separation of concerns favors a standalone module.
5. **Is the three-zone architecture (Source/Governance/Runtime) too complex for Phase 1?** Can we start with a simplified two-zone model?
6. **Should the AdmissionProof be stored alongside the asset or separately?** Alongside is simpler; separately is cleaner separation.
7. **What happens if the trusted public key config is missing or corrupted?** Current design: FAIL CLOSED.

---

*End of Phase 1 Design Document*
