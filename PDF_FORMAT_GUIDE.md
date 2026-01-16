# PDF Format Guide for Statistics Import

## Expected PDF Format

The system expects PDFs in the following format (typical volleyball match reports):

### PDF Structure

```
PAGE HEADER:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MATCH REPORT - [Date] - [Match Name]
Team 1 vs Team 2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEAM SECTION 1: Kuwait SC
─────────────────────────────────────────────────

#  Player Name                Pts  Srv  Rec  Att  Blk  Vote
─────────────────────────────────────────────────
1  Mohamed Al-Azhar            12   8    7    4    2    =
2  Hassan Al-Rashid             8   5    4    2    1    =
3  Abdullah Al-Sabah            16   9    6    5    2    =
4  Khalid Al-Farhan             10   6    5    3    1    =
5  Samir Al-Otaibi               6   4    3    2    0    =
6  Omar Al-Aboody                7   5    2    3    1    =
7  Rashid Al-Hajri               4   3    2    1    0    =
8  Jamal Al-Enezi                5   4    2    2    1    =
9  Abdullah Al-Rashid            3   2    1    1    0    =
10 Mohamed Al-Jasem              2   1    1    0    0    =
11 Waleed Al-Rashid              1   0    0    0    0    =
12 Youssef Al-Otaibi             0   0    0    0    0    =

TEAM SECTION 2: Al Sahel
─────────────────────────────────────────────────

#  Player Name                Pts  Srv  Rec  Att  Blk  Vote
─────────────────────────────────────────────────
1  Ahmed Mansour                 14   7    6    4    2    =
2  Ibrahim Hassan               11   6    5    3    1    =
3  Mahmoud Karim                15   8    7    5    2    =
4  Hassan Amin                   9   5    4    2    1    =
5  Mohamed Nasser               8   4    3    2    0    =
6  Khaled Saleh                  6   3    2    2    1    =
7  Samir Rashid                  5   4    2    1    0    =
8  Omar Hassan                   4   2    1    1    0    =
9  Ahmed Saleh                   2   1    0    0    0    =
10 Waleed Karim                  1   0    0    0    0    =
11 Ali Mohamed                   0   0    0    0    0    =
12 Yousef Karim                  0   0    0    0    0    =
```

## Statistics Field Descriptions

### Field Layout (Left to Right)

| Field | Abbreviation | Description | Extracted As |
|-------|--------------|-------------|--------------|
| Player # | # | Jersey/Player Number | player_number |
| Player Name | Name | Full Name of Player | player_name |
| Points | Pts | Total Points Scored | pts |
| Serve | Srv | Serves Attempted | serve_total |
| Service Errors | - | Errors in serving | serve_err |
| Service Aces | - | Points from serve | serve_ace |
| Reception | Rec | Reception Attempts | reception_total |
| Reception Errors | - | Failed receptions | reception_err |
| Reception Excellent | - | Perfect receptions % | reception_exc |
| Attack | Att | Attack Attempts | attack_total |
| Attack Errors | - | Failed attacks | attack_err |
| Attack Points | - | Points from attack | attack_pts |
| Blocks | Blk | Points from blocking | block_pts |
| Vote | Vote | Player rating/vote | (optional) |

## Supported Variations

The parser handles several PDF variations:

### Variation 1: With Headers
```
Kuwait SC
5  Abdullah Al-Sabah  16 9 6 5 2 =
```

### Variation 2: With Libero Marker
```
5 L Abdullah Al-Sabah  16 9 6 5 2 =
```

### Variation 3: Different Spacing
```
5      Abdullah Al-Sabah           16    9    6    5    2    =
```

### Variation 4: Name with Hyphens/Dots
```
5  Al-Sabah, A.M.  16 9 6 5 2 =
```

## OCR Output Example

When OCR processes the PDF, you might see output like:

```
Kuwait SC

5 Abdullah Al-Sabah 16 9 6 5 2 =
7 Rashid Al-Hajri 4 3 2 1 0 =

Al Sahel

1 Ahmed Mansour 14 7 6 4 2 =
3 Mahmoud Karim 15 8 7 5 2 =
```

## Quality Requirements

### Good PDF Quality ✅
- Clear, crisp text
- High resolution (150+ DPI)
- Black text on white background
- Properly formatted tables
- No excessive compression
- Standard fonts

### Poor PDF Quality ❌
- Blurry or low resolution (< 100 DPI)
- Handwritten entries
- Colored backgrounds
- Heavy compression artifacts
- Non-standard fonts
- Scanned from photocopy

## Debugging OCR Output

To see what the parser extracts from your PDF:

```bash
# Method 1: Using management command
python manage.py test_pdf_upload "file.pdf" --verbose

# Output will show:
# - All extracted lines
# - Matched players
# - Extracted statistics per player
# - Unmatched players for investigation
```

## Common PDF Issues

### Issue 1: Table Layout Not Recognized
**Symptom**: No players extracted
**Solution**: 
- Ensure headers are present (team names)
- Check if data is in table format
- Verify stats are in order: Pts, Srv, Rec, Att, Blk

### Issue 2: Player Names Incorrect
**Symptom**: "Skipped - Player not found"
**Solution**:
- Names must match database exactly (or partially)
- OCR may misread similar letters (l/I, O/0)
- Check PDF for abbreviations

### Issue 3: Missing Statistics
**Symptom**: All stats showing as 0
**Solution**:
- Verify stats columns are in correct order
- Check for non-numeric characters (%, +, -)
- Ensure numbers are not split across lines

### Issue 4: Duplicate Players
**Symptom**: More players than actual teams
**Solution**:
- Remove header/footer rows
- Ensure team headers are distinct
- Check for duplicate entries in PDF

## PDF Conversion Checklist

Before uploading a PDF, verify:

- [ ] **Format**: Is it a valid PDF file?
- [ ] **Quality**: Is text clear and readable?
- [ ] **Resolution**: Is it 150+ DPI?
- [ ] **Content**: Does it contain player statistics?
- [ ] **Teams**: Are both team names clearly labeled?
- [ ] **Players**: Are player numbers visible?
- [ ] **Stats**: Are statistics in clear columns?
- [ ] **Names**: Can you read player names clearly?
- [ ] **Numbers**: Are stats numbers clearly visible?
- [ ] **Size**: Is file < 50MB?

## Expected Parser Output

For a valid PDF, the parser returns:

```python
[
    {
        'player_name': 'Abdullah Al-Sabah',
        'player_number': '5',
        'team': 'Kuwait SC',
        'pts': '16',
        'serve_total': '9',
        'serve_err': '6',
        'serve_ace': '5',
        'reception_total': '0',  # or actual number
        'reception_err': '0',
        'reception_exc': '0',
        'attack_total': '0',
        'attack_err': '0',
        'attack_att': '2',
        'attack_pts': '0',
        'block_pts': '0',
    },
    # ... more players
]
```

## Manual Data Entry Alternative

If PDF extraction fails, you can:

1. **Create test players manually**
   ```bash
   python manage.py shell
   from apps.sport.models.models import Players, Teams
   team = Teams.objects.get(name='Kuwait SC')
   Players.objects.create(name='Abdullah Al-Sabah', number=5, team=team)
   ```

2. **Use admin interface**
   - Go to Players admin
   - Click "Add Player"
   - Fill in details
   - Save

3. **Bulk import via CSV** (if available)
   - Prepare CSV file
   - Use import tool

## Recommended PDF Tools

For preparing PDFs:

- **pdftk**: Merge, split, or reorder pages
- **ImageMagick**: Convert and compress PDFs
- **Ghostscript**: PDF processing
- **PyPDF2**: Python PDF manipulation

Example (compress PDF):
```bash
convert -density 150 input.pdf -quality 80 output.pdf
```

## OCR Enhancement Tips

1. **Pre-process PDF**:
   - Remove images
   - Increase contrast
   - Remove compression artifacts

2. **Use high quality source**:
   - Request original document
   - Avoid photocopies
   - Request scan at 300 DPI

3. **Manual correction**:
   - If OCR misreads, verify manually
   - Update database with correct names
   - Re-run import

## Testing Your PDF

```bash
# 1. Test extraction
python manage.py test_pdf_upload "file.pdf" --verbose

# 2. Review output carefully
# 3. Check for unmatched players
# 4. Fix player names in database if needed
# 5. Run with --apply to save

python manage.py test_pdf_upload "file.pdf" --match=match-slug --apply --verbose
```

## Statistics Calculation Reference

### Serving Efficiency
```
Serve Ace Rate = serve_ace / serve_total * 100%
Serve Error Rate = serve_err / serve_total * 100%
```

### Reception Efficiency
```
Reception Positive % = reception_exc / reception_total * 100%
Reception Error Rate = reception_err / reception_total * 100%
```

### Attack Efficiency
```
Attack Percentage = (attack_pts - attack_err) / attack_total * 100%
```

## Support & Validation

For PDF issues:

1. Check error message
2. Test extraction with utility
3. Review PDF quality
4. Verify player names
5. Check database state
6. Review logs for details

---

## Quick Reference: Field Order

Typical order in PDF statistics tables:
```
# | Name | Pts | Srv | Rec | Att | Blk | Vote
```

If your PDF differs, the parser may need adjustment. Contact support with sample PDF.

---

**Last Updated**: January 2026
**Version**: 1.0

