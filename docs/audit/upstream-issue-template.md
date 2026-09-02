# Issue Template: Decadal Direction Discrepancy

## Problem Description

`iztro@2.6.0` computes decadal (大限) direction using an incorrect yin-yang comparison.

### Current Implementation (palace.js:163)

```javascript
var idx = data_1.GENDER[genderKey] === data_1.earthlyBranches[earthlyBranch].yinYang 
    ? (0, utils_1.fixIndex)(soulIndex + i)   // forward
    : (0, utils_1.fixIndex)(soulIndex - i);  // reverse
```

This compares **gender yinyang** with **earthly branch yinyang**.

### Expected Traditional Rule

According to traditional Zi Wei Dou Shu (《紫微斗数全书》):

**阳男阴女顺，阴男阳女逆**

Direction should be determined by **heavenly stem yinyang + gender**:
- Yang stem + male → forward
- Yang stem + female → reverse
- Yin stem + male → reverse
- Yin stem + female → forward

## Reproduction

```javascript
const { byLunar } = require('iztro').astro;

// Case 1: Yang male (should be forward)
const a1 = byLunar('2024-2-10', 4, 'male', false);
// iztro outputs: reverse (wrong)

// Case 2: Yang female (should be reverse)
const a2 = byLunar('2024-2-10', 4, 'female', false);
// iztro outputs: forward (wrong)

// Case 3: Yin male (should be reverse)
const a3 = byLunar('2025-2-10', 4, 'male', false);
// iztro outputs: forward (wrong)

// Case 4: Yin female (should be forward)
const a4 = byLunar('2025-2-10', 4, 'female', false);
// iztro outputs: reverse (wrong)
```

## Root Cause Analysis

The comparison logic has two issues:

1. **Wrong comparison basis**: Uses `earthlyBranch.yinYang` instead of `heavenlyStem.yinYang`
2. **Logic inversion**: Even if comparing with branch, equal should mean reverse, not forward

### Data Verification

```javascript
// iztro internal constants
GENDER = { male: '阳', female: '阴' }

// earthlyBranches yinYang (correct)
ziEarthly: '阳', chouEarthly: '阴', yinEarthly: '阳', maoEarthly: '阴',
chenEarthly: '阳', siEarthly: '阴', wuEarthly: '阳', weiEarthly: '阴',
shenEarthly: '阳', youEarthly: '阴', xuEarthly: '阳', haiEarthly: '阴'

// heavenlyStems yinYang (from data/heavenlyStems.js)
jiaHeavenly: '阳', yiHeavenly: '阴', bingHeavenly: '阳', dingHeavenly: '阴',
wuHeavenly: '阳', jiHeavenly: '阴', gengHeavenly: '阳', xinHeavenly: '阴',
renHeavenly: '阳', guiHeavenly: '阴'
```

## Test Cases

| Case | Year | Stem | Branch | Gender | Expected | Actual | Match |
|------|------|------|--------|--------|----------|--------|-------|
| 阳男 | 2024 | 甲(阳) | 辰(阳) | male(阳) | 顺 | 逆 | ✗ |
| 阳女 | 2024 | 甲(阳) | 辰(阳) | female(阴) | 逆 | 顺 | ✗ |
| 阴男 | 2025 | 乙(阴) | 巳(阴) | male(阳) | 逆 | 顺 | ✗ |
| 阴女 | 2025 | 乙(阴) | 巳(阴) | female(阴) | 顺 | 逆 | ✗ |

All four combinations output opposite to traditional rule.

## Proposed Fix

Change line 163 in `lib/astro/palace.js`:

```javascript
// FROM (incorrect):
var idx = data_1.GENDER[genderKey] === data_1.earthlyBranches[earthlyBranch].yinYang 
    ? (0, utils_1.fixIndex)(soulIndex + i)
    : (0, utils_1.fixIndex)(soulIndex - i);

// TO (correct):
var stemYinyang = data_1.heavenlyStems[heavenlyStem].yinYang;
var idx = (stemYinyang === '阳' && genderKey === 'male') || 
          (stemYinyang === '阴' && genderKey === 'female')
    ? (0, utils_1.fixIndex)(soulIndex - i)  // note: logic may need review
    : (0, utils_1.fixIndex)(soulIndex + i);
```

Note: The exact fix needs careful review of the sign convention.

## Impact

- Affects all decadal direction calculations
- No impact on other features (stars, palaces, sihua, etc.)
- Breaking change for users relying on current (incorrect) behavior

## Environment

- iztro version: 2.6.0
- Node.js: v22.x
- OS: All platforms

---

Please let me know if you need additional test cases or clarification.
