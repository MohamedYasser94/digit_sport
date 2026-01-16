# Quick Reference: PDF Statistics Upload System

## 🚀 Quick Start

### For End Users (Staff)
1. Go to Match Admin Page
2. Click "Upload PDF Statistics"
3. Select PDF file from computer
4. Click "Upload and Process"
5. Review results on next page

### For Developers

#### Test PDF Extraction
```bash
# Method 1: Management Command (RECOMMENDED)
python manage.py test_pdf_upload "path/to/file.pdf" --verbose

# Method 2: Django Shell
python manage.py shell
from apps.sport.utils.pdf_parser import parse_match_report
stats = parse_match_report("path/to/file.pdf")
```

#### Apply to Specific Match (DRY RUN)
```bash
python manage.py test_pdf_upload "path/to/file.pdf" --match=slug-of-match --verbose
```

#### Actually Save Data
```bash
python manage.py test_pdf_upload "path/to/file.pdf" --match=slug-of-match --apply --verbose
```

## 📁 File Structure

```
apps/sport/
├── views/
│   └── views.py                    # AdminMatchPlayerStaticPdfUpload()
├── utils/
│   └── pdf_parser.py               # parse_match_report()
├── templates/
│   └── good/sport/match/
│       └── statics_pdf.html        # Upload form UI
└── management/commands/
    └── test_pdf_upload.py          # Django command

Root:
├── PDF_UPLOAD_DOCUMENTATION.md     # Full documentation
└── test_pdf_extraction.py          # Standalone test script
```

## 🔧 Configuration

### Requirements (should already be installed)
```
pytesseract>=0.3.10
pdf2image>=1.16.0
Pillow>=9.0.0
```

### Django Settings
```python
# In settings.py - Optional logging configuration
LOGGING = {
    'loggers': {
        'apps.sport.utils.pdf_parser': {
            'level': 'DEBUG',
        },
    },
}
```

## 📊 Data Flow

```
User uploads PDF
        ↓
View saves to temp location
        ↓
OCR extracts text from images
        ↓
Parser matches players
        ↓
Database lookup
        ↓
Save to MatchPlayerReport & PlayerStatics
        ↓
Display results
        ↓
Clean up temp file
```

## ✅ Supported Statistics

### Volleyball Stats (Primary)
- **pts** → point_total: Points scored
- **serve_total**: Serves attempted
- **serve_err**: Serve errors
- **serve_ace**: Aces
- **reception_total**: Receptions attempted
- **reception_err**: Reception errors
- **reception_exc**: Excellent receptions
- **attack_total**: Attacks attempted
- **attack_err**: Attack errors
- **attack_att**: Attack attempts/blocks
- **attack_pts**: Points from attack
- **block_pts**: Points from blocks

## 🐛 Troubleshooting

### Issue: "No statistics found"
```python
# Debug: Check PDF quality
python manage.py test_pdf_upload "file.pdf" --verbose

# Solution: Try different PDF format or higher resolution
```

### Issue: "Players not found"
```python
# Check database for similar names
from apps.sport.models.models import Players
Players.objects.filter(name__icontains='partial_name')

# Solution: Add missing players or update names
```

### Issue: "OCR not working"
```bash
# Install tesseract (system dependency)
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows: Download installer from GitHub
```

### Issue: "Statistics not saved correctly"
```python
# Verify data mapping in view
# Check MatchPlayerReport model fields
# Ensure PlayerStatics has compatible fields
```

## 📝 Key Functions

### Parse Match Report
```python
from apps.sport.utils.pdf_parser import parse_match_report

parsed_stats = parse_match_report(pdf_path)
# Returns: List of dicts with player data
# Example: [
#     {
#         'player_name': 'John Doe',
#         'player_number': '5',
#         'pts': '16',
#         'serve_total': '8',
#         ...
#     }
# ]
```

### View Function
```python
@staff_only
def AdminMatchPlayerStaticPdfUpload(request, match_slug):
    # GET: Shows upload form
    # POST: Processes PDF and saves data
```

## 🎯 Best Practices

1. **Always test first** with dry run
2. **Verify player names** match database before importing
3. **Use high-quality PDFs** for better OCR accuracy
4. **Check results** carefully after upload
5. **Keep backups** of original data

## 📞 Common Commands

```bash
# List matches
python manage.py shell
from apps.sport.models.models import Match
Match.objects.all().values_list('slug', 'name')

# List players for a team
from apps.sport.models.models import Players, Teams
team = Teams.objects.get(name='Kuwait SC')
Players.objects.filter(team=team)

# Check existing stats for a player
from apps.sport.models.operations import MatchPlayerReport
MatchPlayerReport.objects.filter(player__name__contains='name')

# View recent uploads
MatchPlayerReport.objects.all().order_by('-update_at')[:10]
```

## 🔐 Permissions Required

- Staff status
- Access to sport admin
- Permission to modify MatchPlayerReport
- Permission to modify PlayerStatics

## 📈 Performance Notes

- **Small PDFs** (< 5MB): < 1 second
- **Medium PDFs** (5-20MB): 2-5 seconds
- **Large PDFs** (> 20MB): 5-30 seconds
- OCR is CPU intensive - consider background tasks for large batches

## 🔍 Debugging Steps

1. **Check logs**
   ```bash
   tail -f debug.log | grep -i pdf
   ```

2. **Test extraction separately**
   ```bash
   python manage.py test_pdf_upload "file.pdf" --verbose
   ```

3. **Verify database state**
   ```bash
   python manage.py shell
   # Check if players exist, if data was saved, etc.
   ```

4. **Check file permissions**
   ```bash
   ls -la /tmp/
   # Ensure Django process can write to temp directory
   ```

## 📚 Related Models

### MatchPlayerReport
```python
player = ForeignKey(Players)
match = ForeignKey(Match)
point_total, serve_total, attack_total, etc.
static_type = CharField (default: 'General')
```

### PlayerStatics
```python
player = ForeignKey(Players)
Similar statistics fields as MatchPlayerReport
```

### Match
```python
slug = SlugField (unique)
team1, team2 = ForeignKey(Teams)
```

## 🆘 Getting Help

For specific issues, check:
1. `PDF_UPLOAD_DOCUMENTATION.md` - Full documentation
2. `test_pdf_extraction.py` - Standalone test tool
3. Management command help: `python manage.py test_pdf_upload --help`
4. Django logs for detailed error messages

---

**Last Updated**: January 2026
**Version**: 2.0

