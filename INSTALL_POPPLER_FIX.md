# 🔧 INSTALLATION GUIDE: Fix "Poppler Not Installed" Error

## ⚠️ The Error You're Seeing

```
Failed to convert PDF: Unable to get page count. Is poppler installed and in PATH?
```

**Cause**: The `poppler` system library is not installed on your server.

**Solution**: Install the required system dependencies.

---

## 🚀 Quick Fix (Choose Your OS)

### For Ubuntu/Debian (Recommended)
```bash
sudo apt-get update
sudo apt-get install -y poppler-utils tesseract-ocr
```

### For CentOS/RedHat/Fedora
```bash
sudo yum install -y poppler-utils tesseract
```

### For Alpine Linux
```bash
sudo apk add --no-cache poppler-utils tesseract-ocr
```

### For macOS (Homebrew)
```bash
brew install poppler tesseract
```

### For Windows (Manual)
1. Download poppler: https://github.com/oschwartz10612/poppler-windows/releases/
2. Extract to a folder
3. Add to PATH environment variable
4. Download tesseract: https://github.com/UB-Mannheim/tesseract/wiki
5. Install tesseract

---

## ✅ Verify Installation

### Check Poppler
```bash
pdftoimage -v
```
Should show version information.

### Check Tesseract
```bash
tesseract --version
```
Should show version information.

### If Both Work
```bash
python pdf_diagnostic.py "test_file.pdf"
```
Should now work!

---

## 🤖 Automated Installation

Run the provided script:

```bash
bash install_pdf_dependencies.sh
```

This will:
1. ✅ Detect your OS
2. ✅ Install required packages
3. ✅ Verify installation
4. ✅ Show success/error

---

## 📦 What Gets Installed

### poppler-utils
- **Purpose**: Convert PDF to images
- **Used by**: `pdf2image` Python library
- **Contains**: `pdftoimage`, `pdftoppm`, `pdftotext` etc.

### tesseract-ocr
- **Purpose**: Optical Character Recognition (read text from images)
- **Used by**: `pytesseract` Python library
- **Capability**: Extract text from scanned PDFs

---

## 🐍 Python Packages (Already Installed)

These Python packages are already in your requirements.txt:

```
pdf2image>=1.16.0      # Converts PDF to images
pytesseract>=0.3.10    # OCR interface
Pillow>=9.0.0          # Image processing
```

But they need the system libraries to work:
- `pdf2image` needs `poppler`
- `pytesseract` needs `tesseract`

---

## 🔍 Troubleshooting

### Still getting "poppler not installed"

1. **Check installation**:
   ```bash
   which pdftoimage
   ```
   Should show path like `/usr/bin/pdftoimage`

2. **Check PATH environment variable**:
   ```bash
   echo $PATH
   ```
   Should include directory where pdftoimage is located

3. **On Windows**: Add poppler to System PATH
   - Control Panel → System → Advanced → Environment Variables
   - Edit PATH to include poppler directory

### OCR not working

1. **Check tesseract installation**:
   ```bash
   which tesseract
   ```

2. **Test tesseract**:
   ```bash
   tesseract --list-langs
   ```
   Should show: `eng` (English)

3. **If no languages**: Install language files
   ```bash
   sudo apt-get install tesseract-ocr-eng
   ```

---

## 📋 Server Setup Checklist

After installation, verify:

- [ ] `pdftoimage -v` works
- [ ] `tesseract --version` works
- [ ] `python pdf_diagnostic.py "test.pdf"` works
- [ ] Django app can upload PDFs
- [ ] No "poppler" errors in web UI

---

## 🌐 For Shared Hosting / CPanel

If you don't have SSH access:

1. **Contact hosting provider**
   - Ask them to install `poppler-utils` and `tesseract-ocr`
   - Provide them with this guide

2. **Or use alternative hosting**
   - AWS, DigitalOcean, Linode (full SSH access)
   - Heroku, PythonAnywhere (preconfigured)

3. **Workaround while waiting**
   - Manually enter player statistics via admin
   - Use CSV import if available
   - Wait for hosting to install dependencies

---

## 🐳 Docker Setup (If Using Docker)

Add to your Dockerfile:

```dockerfile
FROM python:3.12

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Rest of your setup...
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
```

---

## 🔑 Important Notes

### Minimum Requirements
- ✅ `poppler-utils` - MUST have for PDF conversion
- ✅ `tesseract-ocr` - MUST have for text extraction

### Optional Enhancements
- `tesseract-ocr-eng` - Language pack (usually auto-installed)
- `imagemagick` - Image optimization (not required)

### System Resources
- Poppler: ~5-10 MB disk
- Tesseract: ~20-50 MB disk
- RAM usage: Minimal (< 100 MB per PDF)

---

## ✅ After Installation

Test the system:

### Via Web UI
1. Login to admin
2. Go to Match
3. Click "Upload PDF Statistics"
4. Upload a PDF
5. Should work now! ✅

### Via Command Line
```bash
python manage.py test_pdf_upload "match_report.pdf" --verbose
```

### Via Diagnostic Tool
```bash
python pdf_diagnostic.py "match_report.pdf"
```

---

## 📞 Still Having Issues?

1. **Verify installation**:
   ```bash
   pdftoimage -v && tesseract --version
   ```

2. **Check PATH**:
   ```bash
   which pdftoimage && which tesseract
   ```

3. **Try manual test**:
   ```bash
   python -c "from pdf2image import convert_from_path; print('OK')"
   ```

4. **Check Python packages**:
   ```bash
   pip list | grep -i pdf
   pip list | grep -i tesseract
   ```

5. **Restart Django app** (if using systemd/supervisord)
   ```bash
   sudo systemctl restart digit_sport
   # or
   supervisorctl restart digit_sport
   ```

---

## 🎯 Summary

| Step | Command | Status |
|------|---------|--------|
| 1. Install | `sudo apt-get install poppler-utils tesseract-ocr` | ✅ |
| 2. Verify | `pdftoimage -v && tesseract --version` | ✅ |
| 3. Test | `python pdf_diagnostic.py "file.pdf"` | ✅ |
| 4. Use | Upload PDF via web UI | ✅ |

---

**Status**: ✅ Ready  
**Time to fix**: ~5 minutes  
**Difficulty**: ⭐ Easy  

Once installed, everything will work automatically! 🚀

