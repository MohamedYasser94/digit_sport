# PDF Statistics Save Fix - Summary

## Problem
After extracting PDF data and clicking "Save to Database", player statistics were not being saved to the database. The players showed no data in PlayerStatics.

## Root Cause
The view was using **wrong field names and types**:

1. **Field Name Errors**:
   - Used `pts` instead of `point_total` (model field name)
   - Used non-existent `attack_att` from wrong source (`attack_blo`)
   - Used integer values instead of string values

2. **Type Mismatch**:
   - Models use `CharField` for all stats (not IntegerField)
   - View was passing integers directly instead of converting to strings
   - Database expects: `"16"`, `"25"`, etc., not `16`, `25`

3. **Wrong Mapping**:
   - Old code tried to use `attack_blo` from extractor (doesn't exist)
   - Correct field in extractor is `block_pts`
   - Database field for attack attempts is `attack_att` (not directly populated from extractor)

## Solution Applied

### Changed in `apps/sport/views/views.py` (line ~2207)

**Before (WRONG)**:
```python
defaults = {
    'pts': stats.get('pts', 0),  # ❌ Wrong field name
    'serve_total': stats.get('serve_total', 0),  # ❌ Should be string
    'attack_att': stats.get('attack_blo', 0),  # ❌ Doesn't exist in stats
    # ... etc
}
```

**After (CORRECT)**:
```python
defaults = {
    'point_total': str(stats.get('pts', 0)),  # ✓ Correct field name, converts to string
    'serve_total': str(stats.get('serve_total', 0)),  # ✓ Now converted to string
    'serve_err': str(stats.get('serve_err', 0)),
    'serve_ace': str(stats.get('serve_ace', 0)),
    'reception_total': str(stats.get('reception_total', 0)),
    'reception_err': str(stats.get('reception_err', 0)),
    'reception_exc': str(stats.get('reception_exc', 0)),
    'attack_total': str(stats.get('attack_total', 0)),
    'attack_err': str(stats.get('attack_err', 0)),
    'attack_pts': str(stats.get('attack_pts', 0)),
    'block_pts': str(stats.get('block_pts', 0)),  # ✓ Correct source
    'static_type': 'General'
}
```

## How It Works Now

1. **PDF Upload**: User uploads PDF file
2. **Extraction**: `VolleyballPDFExtractor` parses PDF and returns stats dict with keys like:
   - `pts`, `serve_total`, `serve_err`, `serve_ace`
   - `reception_total`, `reception_err`, `reception_exc`
   - `attack_total`, `attack_err`, `attack_pts`
   - `block_pts`

3. **Preview**: User sees extracted data in table (now shows player names correctly)

4. **Save**: When user clicks "Save to Database":
   - Maps extractor fields to model fields:
     - `pts` → `point_total`
     - `serve_total` → `serve_total`
     - etc.
   - **Converts all values to strings** (required by CharField)
   - Creates/updates both `MatchPlayerReport` and `PlayerStatics` records

5. **Result**: Player stats now visible in player detail page

## Database Models Affected

Both models use CharField for stats:
- `MatchPlayerReport` - stats for single match
- `PlayerStatics` - cumulative stats across all matches

All fields store values as strings: `"16"`, `"25"`, `"0"`, etc.

## Testing

To verify the fix works:

1. **Upload PDF**: Go to Match → Upload PDF Statistics
2. **Review Preview**: Check that player names and numbers show (should be fixed by template update)
3. **Save**: Click "Save to Database"
4. **Verify**: Go to player detail page, should see stats in PlayerStatics table

Expected result after save:
- Player record shows with all stats populated
- Stats match the extracted JSON preview values
- Multiple players updated if all found in database

## Notes

- Players not found in database are skipped (shown in success message)
- If a player number doesn't match, try searching by name (case-insensitive partial match)
- Statistics are saved as **strings**, not integers, per database schema
- Both match-specific and cumulative stats are updated

---

**Fix Date**: January 16, 2026  
**Status**: ✅ COMPLETE
