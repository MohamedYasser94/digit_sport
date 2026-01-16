# PDF Statistics Upload System - Documentation

## Overview
This system allows staff members to upload PDF match reports and automatically extract player statistics, saving them to the database.

## Features

### ✅ Enhanced Features
1. **Robust PDF Parsing**: Uses OCR (Optical Character Recognition) to extract text from PDF images
2. **Intelligent Player Matching**: Matches extracted player names with database records
3. **Detailed Progress Tracking**: Shows real-time feedback on what's being processed
4. **Error Reporting**: Displays specific errors and issues for troubleshooting
5. **Automatic Data Cleaning**: Validates and cleans numerical data
6. **Batch Processing**: Handles multiple players in one upload
7. **Dual Record Updates**: Updates both MatchPlayerReport and PlayerStatics automatically

## File Locations

### Backend View
- **File**: `apps/sport/views/views.py`
- **Function**: `AdminMatchPlayerStaticPdfUpload(request, match_slug)`
- **Line Range**: ~2077-2250

### HTML Template
- **File**: `apps/sport/templates/good/sport/match/statics_pdf.html`
- **Features**: Enhanced UI with progress display and file validation

### PDF Parser
- **File**: `apps/sport/utils/pdf_parser.py`
- **Function**: `parse_match_report(pdf_path)`
- **Features**: OCR-based extraction, improved field matching

### Test Utility
- **File**: `test_pdf_extraction.py`
- **Purpose**: Debug and test PDF extraction locally

## How It Works

### Step 1: Upload
1. Staff member navigates to the PDF upload page
2. Selects a PDF file containing match statistics
3. System validates file type and size (max 50MB)

### Step 2: Processing
```
PDF Upload
    ↓
Save temporarily to disk
    ↓
Extract images from PDF using pdf2image
    ↓
Run OCR using pytesseract
    ↓
Parse text to extract player data
    ↓
Match players with database records
    ↓
Clean and validate statistics
    ↓
Save to MatchPlayerReport
    ↓
Update PlayerStatics
    ↓
Generate detailed report
    ↓
Delete temporary file
```

### Step 3: Results
- Success message with count of updated players
- Warning with list of skipped players
- Error details for debugging

## Database Models

### MatchPlayerReport
- **Purpose**: Stores player statistics for a specific match
- **Key Fields**: 
  - `player` (ForeignKey)
  - `match` (ForeignKey)
  - `point_total`, `serve_total`, `reception_total`, `attack_total`, etc.
  - `static_type` (Default: 'General')

### PlayerStatics
- **Purpose**: Stores cumulative player statistics across all matches
- **Key Fields**: Similar to MatchPlayerReport
- **Usage**: Career statistics, overall performance tracking

## Supported Statistics Fields

The system extracts and stores the following volleyball statistics:

```
Points:
  • pts / point_total: Total points scored

Serving:
  • serve_total: Total serves attempted
  • serve_err: Serving errors
  • serve_ace: Aces (points directly from serve)

Reception:
  • reception_total: Total receptions attempted
  • reception_err: Reception errors
  • reception_exc: Excellent receptions / reception percentage

Attacking:
  • attack_total: Total attacks attempted
  • attack_err: Attack errors
  • attack_att: Attack attempts / blocks against attack
  • attack_pts: Points from attack

Blocking:
  • block_pts: Points from blocking
```

## Error Handling

### Common Issues & Solutions

#### 1. **"No statistics found in the PDF"**
- **Cause**: PDF format not recognized or no data in expected format
- **Solution**: 
  - Ensure PDF is an official match report
  - Check if PDF contains statistics tables
  - Try with a different PDF format

#### 2. **"Skipped N players not found in database"**
- **Cause**: Player names in PDF don't match database records exactly
- **Solution**:
  - Update player names in database to match PDF format
  - Add players to the database before importing statistics
  - Check for spelling differences

#### 3. **"File size exceeds 50MB"**
- **Cause**: PDF file is too large
- **Solution**: 
  - Compress the PDF
  - Use a smaller subset of the document
  - Check file size before uploading

#### 4. **OCR Accuracy Issues**
- **Cause**: Poor PDF quality, scanned images, or complex formatting
- **Solution**:
  - Use higher quality PDF files
  - Ensure PDF is not heavily compressed
  - Try OCR preprocessing in settings

## Configuration

### Dependencies
```
pytesseract: OCR engine interface
pdf2image: PDF to image conversion
Pillow: Image processing
```

### Settings to Configure
The system uses Django's default logging. You can enable debug logging:

```python
# In settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'pdf_parser.log',
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

## Testing

### Using the Test Utility
```bash
# Test a specific PDF
python test_pdf_extraction.py "path/to/file.pdf"

# View available players and matches
python manage.py shell < test_pdf_extraction.py
```

### Debugging
1. Check Django logs for detailed error messages
2. Look for `pdf_parser.log` in the project root
3. Use test utility to verify PDF extraction separately
4. Check if players exist in database with correct names

## Data Validation

The system includes several validation steps:

1. **File Validation**: 
   - Must be .pdf file
   - Max 50MB size
   - Must be readable

2. **Data Validation**:
   - Player name required
   - Numeric fields cleaned (remove non-digits)
   - No negative values
   - Missing data defaults to 0

3. **Database Validation**:
   - Player must exist in database
   - Match must exist in database
   - Proper foreign key relationships

## Performance Considerations

- **Large PDFs**: May take several seconds to process
- **OCR Processing**: CPU intensive, consider running on background task for very large files
- **Database Operations**: Batch updates are optimized with `update_or_create`
- **Temporary Files**: Automatically cleaned up after processing

## Best Practices

1. **PDF Quality**: Use clear, high-resolution PDFs for better OCR accuracy
2. **Player Database**: Keep player names consistent with official records
3. **Testing**: Always test with sample PDFs before production use
4. **Backup**: Have backup of original data before large imports
5. **Validation**: Review reports carefully, especially skipped players and errors

## Future Improvements

Potential enhancements:

1. **Async Processing**: Use Celery for background processing of large PDFs
2. **Advanced OCR**: Implement preprocessing to improve OCR accuracy
3. **Custom Templates**: Support multiple PDF formats
4. **Data Import UI**: Visual preview of extracted data before saving
5. **Batch Operations**: Upload and process multiple PDFs at once
6. **Historical Tracking**: Keep audit trail of all imports

## Support & Troubleshooting

For issues:

1. Check the error message displayed in the UI
2. Review the PDF file for formatting issues
3. Verify player names match database records
4. Check logs for detailed error information
5. Run test utility to isolate the problem
6. Contact development team with specific error details

## URL Endpoints

- **Upload Form**: `/admin/match/<match_slug>/upload-statistics/`
- **Redirect After**: `/admin/match/<match_slug>/players/`

## Permissions

Requires:
- Staff permission
- Access to sport admin area
- Match editing permissions

---

**Last Updated**: January 2026
**Version**: 2.0
**Status**: Production Ready

