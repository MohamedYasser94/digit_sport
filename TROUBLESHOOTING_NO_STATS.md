# Troubleshooting: "No statistics found in the PDF"

## Understanding the Error

When you see this message:
```
❌ No statistics found in the PDF. Please check if the PDF is in the correct format.
```

It means the OCR extraction process didn't find any valid player data. This is usually due to:

1. **PDF Format Issue** - Not a match statistics report
2. **OCR Quality Issue** - Text not readable by OCR
3. **Layout Issue** - Statistics in unexpected format
4. **Team Header Missing** - Can't detect which team owns the data

---

## Quick Diagnostic Steps

### Step 1: Run the Diagnostic Tool
```bash
python pdf_diagnostic.py "your_file.pdf"
```

This will show:
- ✅ File is readable
- ✅ PDF converts to images
- ✅ OCR text extraction
- ✅ What text the OCR sees
- ✅ Why parsing might fail

### Step 2: Check the Debug Output
The diagnostic tool shows the actual OCR text. Look for:
- Player numbers (5, 10, etc.)
- Player names (Abdullah, Ahmed, etc.)
- Statistics numbers (points, serves, etc.)
- Team names (Kuwait SC, Al Sahel, etc.)

### Step 3: Review the PDF

Open the PDF in a reader and check:

#### ✅ Good PDF Format
```
Kuwait SC
5  Abdullah Al-Sabah        16  9  6  5  2
10 Ahmed Mansour           12  7  5  3  1
1  Mohamed Hassan           8  5  4  2  1

Al Sahel
1  Hassan Karim            14  8  6  5  2
3  Mahmoud Ibrahim         15  9  7  5  2
```

#### ❌ Problems to Watch For

1. **No Team Headers**
   - If PDF doesn't show "Kuwait SC" or team names
   - Solution: Add team headers manually or use different PDF

2. **Scanned Image Instead of Text**
   - If selecting text doesn't work in PDF viewer
   - Solution: Use OCR-processed version of PDF

3. **Heavily Compressed**
   - If text looks blurry or pixelated
   - Solution: Get higher quality PDF

4. **Data in Different Format**
   - If stats are in columns instead of rows
   - Solution: Verify PDF is official match report

5. **Non-English Characters**
   - If names use special characters/Arabic
   - Solution: Check if OCR can read them (may need settings change)

---

## Solutions

### Solution 1: Verify PDF Format

Check that your PDF contains:

✅ **Must Have:**
- Team name header (Kuwait SC, Al Sahel, etc.)
- Player number (1-14)
- Player name
- At least 1 statistic (points, serves, etc.)

✅ **Should Have:**
- Multiple players (4+)
- Multiple statistics (5+)
- Clear text layout

❌ **Problems:**
- No team headers → Add them or mark team data somehow
- Scanned image → Convert to text-based PDF
- Empty or missing data → Incomplete report
- Random text → Not a match report

### Solution 2: Improve PDF Quality

If PDF is hard to read:

**On Linux/Mac:**
```bash
# Increase resolution and enhance contrast
convert -density 200 input.pdf -quality 90 output.pdf
```

**On Windows:**
```bash
# Use Ghostscript (install first)
gswin64c -sDEVICE=pdfwrite -dDEVICEWIDTHPOINTS=612 -dDEVICEHEIGHTPOINTS=792 ^
  -dNOPAUSE -dBATCH -dSAFER -r200 -sOutputFile=output.pdf input.pdf
```

**Using Online Tools:**
1. Go to smallpdf.com or ilovepdf.com
2. Use "Compress PDF" to remove unnecessary data
3. Download improved version

### Solution 3: Use Diagnostic Output

Run the diagnostic and read what was extracted:

```bash
python pdf_diagnostic.py "match_report.pdf"
```

Look at the "OCR OUTPUT" section. You'll see exactly what the parser sees:

```
Page 1:
  [1] Kuwait SC
  [2] 5 Abdullah Al-Sabah 16 9 6 5 2
  [3] 10 Ahmed Mansour 12 7 5 3 1
  ...
```

If this looks correct but still fails, it's a parsing regex issue (contact support).

### Solution 4: Manual Data Entry

If PDF extraction continues to fail:

1. **Via Admin Interface:**
   - Go to Players admin
   - Manually add/edit each player's statistics
   - Takes ~5 minutes for a full match

2. **Via Management Command:**
   ```bash
   python manage.py shell
   from apps.sport.models.models import Players, Match
   from apps.sport.models.operations import MatchPlayerReport
   
   player = Players.objects.get(name='Abdullah Al-Sabah')
   match = Match.objects.get(slug='match-slug')
   
   MatchPlayerReport.objects.create(
       player=player,
       match=match,
       point_total='16',
       serve_total='9',
       # ... other fields
   )
   ```

### Solution 5: Contact Support

If none of these work, provide:

1. Run the diagnostic:
   ```bash
   python pdf_diagnostic.py "file.pdf" > diagnostic_output.txt
   ```

2. Share the diagnostic output
3. Share the PDF file if possible
4. Describe what's in the PDF

---

## Advanced: Enable Debug Logging

To see detailed parsing information:

### Option 1: Check Console Output

The enhanced parser now prints debug output:
```bash
python manage.py test_pdf_upload "file.pdf" --verbose
```

Look for lines like:
```
[DEBUG] Page 1 OCR output (first 500 chars):
...
[DEBUG] Team detected: Kuwait SC from line: Kuwait SC
[DEBUG] Matched: #5 Abdullah Al-Sabah, stats: ['16', '9', '6', '5', '2']
```

### Option 2: Enable File Logging

Edit `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'pdf_debug.log',
        },
    },
    'loggers': {
        'apps.sport.utils.pdf_parser': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

Then check `pdf_debug.log` for detailed output.

---

## PDF Examples & Samples

### What the Parser Expects

```
MATCH REPORT - Volleyball

Kuwait SC
────────────────────────────────────────────
#  Name                      Pts Srv Rec Att Blk
────────────────────────────────────────────
1  Mohamed Hassan            12  8  7  4  2
2  Hassan Al-Rashid           8  5  4  2  1
3  Abdullah Al-Sabah         16  9  6  5  2
4  Khalid Al-Farhan          10  6  5  3  1
5  Samir Al-Otaibi            6  4  3  2  0

Al Sahel
────────────────────────────────────────────
#  Name                      Pts Srv Rec Att Blk
────────────────────────────────────────────
1  Ahmed Mansour             14  7  6  4  2
2  Ibrahim Hassan            11  6  5  3  1
3  Mahmoud Karim             15  8  7  5  2
```

### What the Parser Can Handle

✅ Missing some statistics (will default to 0)
✅ Extra spaces between numbers
✅ Libero marker (L prefix)
✅ Names with hyphens or dots
✅ Different team names (if they appear at start of line)
✅ Multiple pages
✅ Slight OCR variations (7 vs 1, 0 vs O)

### What the Parser Cannot Handle

❌ No team headers
❌ Heavily scanned/compressed
❌ Statistics in completely different format
❌ No player numbers
❌ No player names
❌ Unreadable/blurry text

---

## Recommended PDF Format

Best results with:

1. **Source**
   - Official digital match report
   - Printed and scanned at 200+ DPI
   - Clear, crisp text

2. **Content**
   - Team name (Kuwait SC, Al Sahel, etc.)
   - Player number (1-14)
   - Player name (full or partial)
   - Statistics (points, serves, reception, etc.)

3. **Layout**
   - Simple table format
   - One player per row
   - Numbers and names clearly separated

4. **Quality**
   - Black text on white background
   - No background images
   - Good contrast
   - Not heavily compressed

---

## Testing Your PDF

### Test 1: Basic Readability
```bash
python pdf_diagnostic.py "file.pdf" | head -30
```
Shows if PDF is readable.

### Test 2: OCR Works
```bash
python pdf_diagnostic.py "file.pdf" | grep -A 5 "Page 1"
```
Shows if OCR extracts text.

### Test 3: Data Extraction
```bash
python manage.py test_pdf_upload "file.pdf" --verbose
```
Shows if parser finds players.

### Test 4: Database Save
```bash
python manage.py test_pdf_upload "file.pdf" --match=slug --apply --verbose
```
Actually saves data if everything works.

---

## Comparison: Other Solutions

| Method | Pros | Cons |
|--------|------|------|
| **PDF Upload** | Fast, bulk import | Needs good PDF format |
| **Manual Entry** | Always works | Slow, error-prone |
| **CSV Import** | Structured, reliable | Requires CSV file |
| **API** | Programmatic | Requires programming |
| **Admin Interface** | Simple UI | Tedious for many records |

---

## Checklist for Success

Before uploading, verify:

- [ ] PDF opens in reader (not corrupted)
- [ ] Text can be selected (not scanned image)
- [ ] Team names visible (Kuwait SC, Al Sahel, etc.)
- [ ] Player numbers visible (1, 2, 3, etc.)
- [ ] Player names visible (names readable)
- [ ] Statistics visible (numbers for each stat)
- [ ] File size < 50MB
- [ ] Text is clear and crisp (not blurry)
- [ ] Good contrast (black on white)

---

## Still Having Issues?

1. ✅ Run: `python pdf_diagnostic.py "file.pdf"`
2. ✅ Check: Output shows what OCR sees
3. ✅ Verify: PDF format matches examples above
4. ✅ Try: Improving PDF quality
5. ✅ Consider: Manual data entry as alternative
6. ✅ Ask: Support team with diagnostic output

---

**Version**: 1.0  
**Last Updated**: January 16, 2026

For more help, see:
- `PDF_FORMAT_GUIDE.md` - PDF specifications
- `QUICK_REFERENCE_PDF.md` - Quick start
- `PDF_UPLOAD_DOCUMENTATION.md` - Complete reference

