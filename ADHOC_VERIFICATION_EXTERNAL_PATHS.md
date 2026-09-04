# External Paths Fix - Ad-hoc Verification

**Date**: 2026-09-03 22:45
**Type**: Ad-hoc verification (targeted)

---

## Changes

| File | Fix |
|------|-----|
| `src/tongshu/corpus/adapter.py` | Path → project-relative |
| `src/tongshu/corpus/validation.py` | Path → project-relative |
| `src/tongshu/k2g/concepts/generate_concepts.py` | Path → project-relative |
| `src/tongshu/k2g/registry_loader.py` | Path → project-relative |
| `src/tongshu/v_validation/end_to_end.py` | Path → project-relative |
| `tests/chain/test_evidence_chain.py` | cwd → project path |

## Verification

```
[1] FOR-BAZI data files...  ✅ 6/6 present
[2] Adapter path resolution ✅ Correct
[3] Data loading...         ✅ 7047 entries loaded
[4] Query methods...        ✅ DTS=719, sample OK
[5] Core tests...           ✅ 60 passed in 8.72s

PASSED: 10/10
✅ ALL CHECKS PASSED
```

## Notes

- Only docstring references remain (non-executable)
- FOR-BAZI data now local to project (5.8MB)
- Temp script cleaned up
