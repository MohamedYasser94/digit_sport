#!/bin/bash
# Install dependencies for PDF processing on Linux/Unix servers

echo "Installing PDF processing dependencies..."
echo "==========================================="

# Detect OS
if [ -f /etc/debian_version ]; then
    # Debian/Ubuntu
    echo "Detected Debian/Ubuntu system"
    echo "Installing poppler-utils and other dependencies..."
    sudo apt-get update
    sudo apt-get install -y poppler-utils
    sudo apt-get install -y tesseract-ocr

elif [ -f /etc/redhat-release ]; then
    # RedHat/CentOS/Fedora
    echo "Detected RedHat/CentOS system"
    echo "Installing poppler-utils and other dependencies..."
    sudo yum install -y poppler-utils
    sudo yum install -y tesseract

elif [ -f /etc/alpine-release ]; then
    # Alpine Linux
    echo "Detected Alpine Linux"
    echo "Installing poppler-utils and other dependencies..."
    sudo apk add --no-cache poppler-utils
    sudo apk add --no-cache tesseract-ocr

else
    echo "Unknown OS. Please install manually:"
    echo "  - poppler-utils (for pdf2image)"
    echo "  - tesseract-ocr (for OCR)"
    exit 1
fi

echo ""
echo "Verification..."
echo "==========================================="

# Verify installations
if command -v pdftoimage &> /dev/null; then
    echo "✅ poppler-utils installed: $(pdftoimage -v 2>&1 | head -1)"
else
    echo "❌ poppler-utils NOT found"
    exit 1
fi

if command -v tesseract &> /dev/null; then
    echo "✅ tesseract-ocr installed: $(tesseract --version | head -1)"
else
    echo "❌ tesseract-ocr NOT found"
    exit 1
fi

echo ""
echo "✅ All dependencies installed successfully!"
echo ""
echo "You can now:"
echo "  • Upload PDFs via the web interface"
echo "  • Run: python manage.py test_pdf_upload \"file.pdf\""
echo "  • Run: python pdf_diagnostic.py \"file.pdf\""

