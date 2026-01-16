# Testing Walkthrough: PDF Statistics Upload

## Overview
This guide walks through testing the PDF statistics upload system step by step.

## Prerequisites
- Staff access to admin panel
- Sample PDF file with volleyball statistics
- At least 2 test players in database
- Django project running locally

## Part 1: Setup & Preparation

### Step 1: Create Test Players (if needed)
```bash
python manage.py shell
```

```python
from apps.sport.models.models import Teams, Players, Match

# Create or get teams
kuwait_team, _ = Teams.objects.get_or_create(
    name='Kuwait SC',
    defaults={'country': 'Kuwait', 'city': 'Kuwait City'}
)
sahel_team, _ = Teams.objects.get_or_create(
    name='Al Sahel',
    defaults={'country': 'Kuwait', 'city': 'Kuwait City'}
)

# Create test players
players_data = [
    {'name': 'Abdullah Al-Sabah', 'number': 5, 'team': kuwait_team},
    {'name': 'Hassan Al-Rashid', 'number': 2, 'team': kuwait_team},
    {'name': 'Ahmed Mansour', 'number': 1, 'team': sahel_team},
    {'name': 'Mahmoud Karim', 'number': 3, 'team': sahel_team},
]

for data in players_data:
    Players.objects.get_or_create(
        name=data['name'],
        number=data['number'],
        team=data['team']
    )

print("✅ Test players created")
exit()
```

### Step 2: Create or Get a Test Match
```bash
python manage.py shell
```

```python
from apps.sport.models.models import Match, Teams
from datetime import datetime

kuwait_team = Teams.objects.get(name='Kuwait SC')
sahel_team = Teams.objects.get(name='Al Sahel')

match, _ = Match.objects.get_or_create(
    slug='test-match-001',
    defaults={
        'team1': kuwait_team,
        'team2': sahel_team,
        'match_date': datetime.now(),
        'status': 'FINISHED'
    }
)

print(f"✅ Test match created: {match.slug}")
exit()
```

## Part 2: Test via Management Command

### Test 1: Test Extraction Only
```bash
# Copy sample PDF to project root first
python manage.py test_pdf_upload "path/to/sample.pdf" --verbose
```

**Expected Output**:
```
======================================================================
PDF Extraction Test
======================================================================

📄 Parsing PDF...
✅ Found 12 players

Extracted Data:
──────────────────────────────────────────────────────────────────────

[1] 5 - Abdullah Al-Sabah
    pts: 16
    serve_total: 9
    ...
```

**What to verify**:
- ✓ Player count matches PDF
- ✓ Player names are readable
- ✓ Statistics are numeric
- ✓ No parsing errors

### Test 2: Test Database Matching
```bash
python manage.py test_pdf_upload "path/to/sample.pdf" --verbose
```

Look for the "Database Matching:" section

**Expected Output**:
```
Database Matching:
──────────────────────────────────────────────────────────────────────

✅ Abdullah Al-Sabah → Abdullah Al-Sabah (ID: 123)
✅ Hassan Al-Rashid → Hassan Al-Rashid (ID: 124)
⚠️  Unknown Player - NOT FOUND
```

**What to verify**:
- ✓ Players in database are matched
- ✓ Unknown players are identified
- ✓ Match count is accurate

### Test 3: Dry Run (No Database Changes)
```bash
python manage.py test_pdf_upload "path/to/sample.pdf" --match=test-match-001 --verbose
```

**Expected Output**:
```
⚠️ DRY RUN: Use --apply flag to save to database
```

**What to verify**:
- ✓ No database changes made
- ✓ Dry run message shown

### Test 4: Apply Changes to Database
```bash
python manage.py test_pdf_upload "path/to/sample.pdf" --match=test-match-001 --apply --verbose
```

**Expected Output**:
```
Saving to Database:
──────────────────────────────────────────────────────────────────────

✅ Saved: Abdullah Al-Sabah
✅ Saved: Hassan Al-Rashid
⏭️  Skipping (not found): Unknown Player

======================================================================
Successfully saved 2 records
```

**What to verify**:
- ✓ Records saved successfully
- ✓ Correct count of saved records
- ✓ Unmatched players listed

## Part 3: Test via Web UI

### Test 5: Access Upload Page
1. Login to admin panel
2. Navigate to Match List
3. Find test match "test-match-001"
4. Click "Upload PDF Statistics" (or similar button)

**Expected Result**:
- ✓ Upload form displays
- ✓ Match name shown
- ✓ Teams information displayed
- ✓ File input field present

### Test 6: File Validation
1. Try uploading non-PDF file
   - **Expected**: Error message "Please select a PDF file"
2. Try uploading file > 50MB
   - **Expected**: Error message "File size exceeds 50MB limit"
3. Select valid PDF file
   - **Expected**: File info displayed (name, size)
   - **Expected**: Upload button becomes enabled

**Verify**:
- ✓ File type validation works
- ✓ File size validation works
- ✓ File info displays correctly
- ✓ Button state changes appropriately

### Test 7: Successful Upload
1. Select valid PDF with test data
2. Click "Upload and Process"
3. Wait for processing (1-10 seconds)

**Expected Result**:
- ✓ Loading indicator shown
- ✓ Redirect to player list page
- ✓ Success message displayed at top
- ✓ Message shows player count

**Example Message**:
```
✓ Successfully updated statistics for 2 players out of 4 found in PDF.
⚠ Skipped 2 players not found in database:
  • Unknown Player 1
  • Unknown Player 2
```

### Test 8: Verify Database Changes
1. Click on first player from updated list
2. Check "Match Player Report" statistics
   - **Verify**: Statistics match PDF values
   - **Verify**: Point total matches
   - **Verify**: All stat fields populated

3. Check "Player Statics" (overall player stats)
   - **Verify**: Statistics updated
   - **Verify**: Same values as MatchPlayerReport

```bash
# Or via Django shell
python manage.py shell

from apps.sport.models.operations import MatchPlayerReport
from apps.sport.models.models import Match

match = Match.objects.get(slug='test-match-001')
reports = MatchPlayerReport.objects.filter(match=match)

for report in reports:
    print(f"{report.player.name}:")
    print(f"  Points: {report.point_total}")
    print(f"  Serves: {report.serve_total}")
    print(f"  Attacks: {report.attack_total}")
```

## Part 4: Error Handling Tests

### Test 9: Empty PDF
1. Create empty PDF file
2. Upload via web UI
3. **Expected**: Error message "No statistics found in the PDF"

### Test 10: Corrupted PDF
1. Create corrupted PDF (rename text file to .pdf)
2. Upload via web UI
3. **Expected**: Error message about PDF processing

### Test 11: Unmatched Players
1. Create PDF with random player names
2. Upload via web UI
3. **Expected**: 
   - ✓ No players updated
   - ✓ Warning message shown
   - ✓ All players listed as skipped

### Test 12: Partial Match
1. Create PDF with mix of known and unknown players
2. Upload via web UI
3. **Expected**:
   - ✓ Known players updated
   - ✓ Unknown players skipped
   - ✓ Both counts shown in message

## Part 5: Data Validation Tests

### Test 13: Statistics Accuracy
1. Get PDF with known statistics
2. Upload and check extracted values

```bash
# Check extracted value
python manage.py test_pdf_upload "file.pdf" --verbose | grep "pts:"

# Should show correct point values
```

### Test 14: Field Mapping
1. Upload PDF
2. Check database record
3. Verify each field:

```python
from apps.sport.models.operations import MatchPlayerReport

report = MatchPlayerReport.objects.first()
print(f"point_total: {report.point_total}")      # From 'pts'
print(f"serve_total: {report.serve_total}")      # From 'serve_total'
print(f"attack_pts: {report.attack_pts}")        # From 'attack_pts'
print(f"block_pts: {report.block_pts}")          # From 'block_pts'
```

## Part 6: Edge Cases

### Test 15: Special Characters in Names
1. Test with names containing: hyphens, dots, apostrophes
2. **Expected**: Names parsed correctly

### Test 16: Missing Statistics
1. Test with PDF having incomplete stats
2. **Expected**: Missing stats default to 0

### Test 17: Duplicate Entries
1. Upload same PDF twice
2. **Expected**: Records updated, not duplicated (update_or_create)

### Test 18: Concurrent Uploads
1. Upload two PDFs in quick succession
2. **Expected**: Both processed correctly

## Verification Checklist

### Functionality
- [ ] PDF upload works
- [ ] File validation works
- [ ] OCR extraction works
- [ ] Player matching works
- [ ] Database saves correctly
- [ ] Statistics display correctly
- [ ] Error messages show

### Database
- [ ] MatchPlayerReport created
- [ ] MatchPlayerReport updated on re-upload
- [ ] PlayerStatics created
- [ ] PlayerStatics updated on re-upload
- [ ] Foreign keys correct
- [ ] All fields populated

### UI/UX
- [ ] Upload form displays
- [ ] File info shows
- [ ] Loading state works
- [ ] Messages display
- [ ] Button states correct
- [ ] Team info shows
- [ ] Instructions clear

### Error Handling
- [ ] Invalid files rejected
- [ ] Errors reported clearly
- [ ] System doesn't crash
- [ ] Recovery is graceful
- [ ] Logs are helpful

### Performance
- [ ] Upload completes in < 30 seconds
- [ ] UI remains responsive
- [ ] No memory leaks
- [ ] Temp files cleaned up

## Troubleshooting During Testing

### Issue: "PDF parsing error"
```bash
# Check if tesseract is installed
tesseract --version

# If not installed:
# Ubuntu/Debian: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract
# Windows: Download from GitHub
```

### Issue: "No players found"
```bash
# Check OCR output
python manage.py test_pdf_upload "file.pdf" --verbose

# Look for extracted text to debug
```

### Issue: "Players not matching"
```bash
# Check player names in database
python manage.py shell
from apps.sport.models.models import Players
Players.objects.values_list('name', flat=True)[:10]

# Compare with PDF names
# Update names if different
```

### Issue: "Database not updating"
```bash
# Check model fields
python manage.py shell
from apps.sport.models.operations import MatchPlayerReport
report = MatchPlayerReport.objects.first()
print(report.__dict__)

# Verify all fields have values
```

## Final Validation

### Sign-Off Checklist
- [ ] All tests passed
- [ ] No errors encountered
- [ ] Data accuracy verified
- [ ] UI looks good
- [ ] Performance acceptable
- [ ] Documentation accurate
- [ ] Ready for production

## Performance Baseline

Record your test results:

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| PDF extraction | < 2 sec | ___ | ✓/✗ |
| Player matching | < 1 sec | ___ | ✓/✗ |
| Database save | < 2 sec | ___ | ✓/✗ |
| Total process | < 5 sec | ___ | ✓/✗ |

## Support & Issues

If you encounter issues:
1. Check error message carefully
2. Review logs: `tail -f debug.log`
3. Run test utility for more details
4. Check database state with Django shell
5. Review documentation

---

**Testing Guide Version**: 1.0
**Created**: January 2026
**Last Updated**: January 16, 2026

