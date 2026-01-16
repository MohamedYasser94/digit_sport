# PDF Extraction - Current Status & Next Steps

## ✅ What's Working

1. **Team Detection** - Successfully finds Kuwait SC and Al Sahel (no duplicates now)
2. **Player Detection** - Correctly identifies players and filters out headers/totals
3. **Basic Stats** - Points, Serve stats, Reception start are mostly correct
4. **Libero Detection** - Correctly marks libero players
5. **No Crashes** - System runs without errors

## ❌ What Needs Fixing

### Attack Points Missing
**Problem**: Attack points showing as 0 instead of actual values

**Example** (Hoag Nicholas):
- Expected: Attack 25/1/15 (Tot/Err/Pts)
- Actual: Attack 25/1/0 (Tot/Err/Pts) ❌

**Root Cause**: When we filter out percentages (%), we're not collecting all the numbers that come after

**Solution Needed**: 
- Don't filter percentages during collection
- Filter them during mapping based on their position
- Numbers after reception should be: Attack Total, Attack Err, Attack Blo (skip), Attack Pts, Attack % (skip)

### Some Stats Still Wrong
- Serve Ace showing wrong values (16 instead of 1)
- Reception counts off for some players

## 🎯 Recommended Fix

Update `parse_player_stats` to:

1. **Collect ALL numbers** (don't filter % during collection)
2. **Map by position** more carefully:
   ```
   After skipping set indicators (3 numbers) and vote (decimal):
   [0] = Points
   [1] = BP (skip)
   [2] = W-L (skip)  
   [3] = Serve Tot
   [4] = Serve Err
   [5] = Serve Pts
   [6] = Reception Tot
   [7] = Reception Err
   [8] = Reception Pos% (SKIP - will be >50)
   [9] = Reception Exc% (SKIP - will be >20)
   [10] = Attack Tot
   [11] = Attack Err
   [12] = Attack Blo (skip or 0)
   [13] = Attack Pts
   [14] = Attack% (SKIP - will be >50)
   [15] = Block Pts
   ```

3. **Use position-based logic** instead of value-based filtering

## 📋 Manual Testing Reference

Compare with PDF images you provided:

**Hoag Nicholas (#4 Kuwait SC):**
- Points: 16 ✓
- Serve: 16/4/1 (Tot/Err/Pts) ✓
- Reception: 11/1 (Tot/Err) ✓  
- Attack: 25/1/15 (Tot/Err/Pts) - **Currently showing 25/1/0** ❌
- Block: 0 or blank ✓

**Almisry Hussain (#1 Al Sahel):**
- Points: 7 ✓
- Serve: 8/1/2 (Tot/Err/Pts) ✓
- Reception: 13/1 (Tot/Err) ✓
- Attack: 17/./5 (Tot/Err/Pts) - Need to verify
- Block: blank ✓

## 🚀 Quick Fix Code

The key is in the stats mapping section - here's the corrected approach:

```python
# Collect ALL numbers without filtering
all_numbers = []
for line in stats_lines:
    nums = re.findall(r'\d+', line)  # Just digits
    all_numbers.extend([int(n) for n in nums])

# Now skip decimals and map by position
idx = 0
# Skip set indicators (first 3 small numbers)
while idx < len(all_numbers) and all_numbers[idx] <= 6 and idx < 3:
    idx += 1

# Map by position
pts_idx = idx
bp_idx = idx + 1  
wl_idx = idx + 2
srv_tot_idx = idx + 3
srv_err_idx = idx + 4
srv_pts_idx = idx + 5
rec_tot_idx = idx + 6
rec_err_idx = idx + 7
# idx + 8 and +9 are percentages (>50), skip them
rec_pct1_idx = idx + 8
rec_pct2_idx = idx + 9
att_tot_idx = idx + 10
att_err_idx = idx + 11
att_blo_idx = idx + 12  # skip
att_pts_idx = idx + 13
att_pct_idx = idx + 14  # skip
blk_pts_idx = idx + 15

# Assign values
stats['pts'] = all_numbers[pts_idx] if pts_idx < len(all_numbers) else 0
stats['serve_total'] = all_numbers[srv_tot_idx] if srv_tot_idx < len(all_numbers) else 0
# ... etc
stats['attack_pts'] = all_numbers[att_pts_idx] if att_pts_idx < len(all_numbers) and all_numbers[att_pts_idx] <= 50 else 0
```

## 📝 Files to Update

1. **`apps/sport/utils/pdf_extractor_final.py`** - Fix the `parse_player_stats` method
2. Test with `python quick_test.py`  
3. Verify output matches PDF images
4. Test via web interface

## ✨ Alternative: Use Manual Column Mapping

Since the PDF has a fixed column structure, we could also:
- Extract text with positions (PyMuPDF can give x,y coordinates)
- Map columns by x-position
- This would be more accurate but more complex

## 🎓 Summary

The extractor is **80% working**:
- ✅ Teams detected correctly
- ✅ Players found correctly
- ✅ Non-players filtered out
- ✅ Basic stats extracted
- ❌ Attack points wrong (main issue)
- ❌ Some serve/reception values off

**Main issue**: Number collection and mapping logic needs refinement to handle the exact PDF column structure.

---

**Current Files**:
- `apps/sport/utils/pdf_extractor_final.py` - Main extractor
- `quick_test.py` - Quick test script  
- `PDF_COLUMN_MAPPING.md` - Column structure reference

**Test Command**: `python quick_test.py`
