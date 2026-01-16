"""
Find player lines in raw PDF
"""
import fitz
import re

pdf_path = r"C:\Users\mhitl\PycharmProjects\digit_sport\KNL 21 25-12-28 Kuwait SC 3x0 Al Sahel - Match report.pdf"

doc = fitz.open(pdf_path)
page = doc[0]
text = page.get_text("text")

lines = text.split('\n')

print("Looking for Hoag Nicholas...")
for i, line in enumerate(lines):
    if 'Hoag' in line or 'Nicholas' in line or (re.match(r'^\d+$', line.strip()) and i < len(lines) - 1 and 'Hoag' in lines[i+1]):
        # Print context
        start = max(0, i-2)
        end = min(len(lines), i+10)
        print(f"\n Found at line {i}:")
        for j in range(start, end):
            marker = " <--" if j == i else ""
            print(f"{j:3d}: |{lines[j]}|{marker}")
        break

doc.close()
