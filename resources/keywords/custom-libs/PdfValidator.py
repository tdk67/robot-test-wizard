"""
PdfValidator.py
Custom Robot Framework library for inspecting, parsing, and converting PDF documents.
Uses pypdf for fast, headless, pure-Python text extraction and structure parsing.
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from pypdf import PdfReader
from robot.api.deco import keyword, library

@library(scope='GLOBAL')
class PdfValidator:
    """Library for extracting and converting PDF documents to structured XML."""

    @keyword
    def extract_pdf_text(self, pdf_path: str) -> str:
        """
        Extracts all textual content from the given PDF file.
        
        Example:
        | ${text}= | Extract Pdf Text | ${OUTPUT_DIR}/receipt.pdf |
        """
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file does not exist: {pdf_path}")
        
        reader = PdfReader(str(path))
        pages_text = []
        for index, page in enumerate(reader.pages):
            extracted = page.extract_text() or ""
            pages_text.append(extracted)
            
        full_text = "\n".join(pages_text)
        return full_text

    @keyword
    def convert_pdf_to_xml(self, pdf_path: str) -> str:
        """
        Converts the content of a PDF file into a structured XML string.
        Automatically parses structured receipts (headers, line items, prices, totals)
        while preserving complete page/line text hierarchy for generic XPath queries.
        
        Example XML structure:
        <receipt>
            <title>BrowserStack Demo</title>
            <items>
                <item>
                    <brand>Samsung</brand>
                    <type>Galaxy S9</type>
                    <quantity>1</quantity>
                    <price>$699.00</price>
                </item>
                <item>
                    <brand>Apple</brand>
                    <type>iPhone 12</type>
                    <quantity>1</quantity>
                    <price>$799.00</price>
                </item>
            </items>
            <total_price>$1498.00</total_price>
            <pages>
                <page number="1">
                    <line>BrowserStack Demo</line>
                    <line>Brand Type Quantity Price</line>
                    ...
                </page>
            </pages>
        </receipt>
        """
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file does not exist: {pdf_path}")
            
        reader = PdfReader(str(path))
        root = ET.Element('receipt')
        
        pages_elem = ET.SubElement(root, 'pages')
        all_lines = []
        for p_idx, page in enumerate(reader.pages):
            page_elem = ET.SubElement(pages_elem, 'page', number=str(p_idx + 1))
            extracted = page.extract_text() or ""
            for raw_line in extracted.split('\n'):
                line = raw_line.strip()
                if line:
                    line_elem = ET.SubElement(page_elem, 'line')
                    line_elem.text = line
                    all_lines.append(line)

        if all_lines:
            title_elem = ET.SubElement(root, 'title')
            title_elem.text = all_lines[0]
            
        items_elem = ET.SubElement(root, 'items')
        
        # Regex matching: Brand (word), Type (words), Quantity (int), Price (starts with $)
        # e.g.: "Samsung Galaxy S9 1 $699.00.00"
        item_regex = re.compile(r'^(\S+)\s+(.+?)\s+(\d+)\s+(\$\d+(?:\.\d+)*)$')
        
        for line in all_lines:
            lower = line.lower()
            if 'total price:' in lower:
                tot_match = re.search(r'total price:\s*(\$\d+(?:\.\d+)*)', line, re.IGNORECASE)
                tot_val = tot_match.group(1) if tot_match else line.split(':')[-1].strip()
                clean_tot = re.sub(r'(\.\d{2})\.00$', r'\1', tot_val)
                tot_elem = ET.SubElement(root, 'total_price')
                tot_elem.text = clean_tot
            else:
                m = item_regex.match(line)
                if m:
                    item_elem = ET.SubElement(items_elem, 'item')
                    b_elem = ET.SubElement(item_elem, 'brand')
                    b_elem.text = m.group(1)
                    
                    t_elem = ET.SubElement(item_elem, 'type')
                    t_elem.text = m.group(2)
                    
                    q_elem = ET.SubElement(item_elem, 'quantity')
                    q_elem.text = m.group(3)
                    
                    p_elem = ET.SubElement(item_elem, 'price')
                    clean_price = re.sub(r'(\.\d{2})\.00$', r'\1', m.group(4))
                    p_elem.text = clean_price

        return ET.tostring(root, encoding='utf-8').decode('utf-8')

    @keyword
    def verify_pdf_contains(self, pdf_path: str, *expected_strings: str):
        """
        Asserts that the PDF at `pdf_path` contains each of the given strings.
        
        Example:
        | Verify Pdf Contains | ${OUTPUT_DIR}/receipt.pdf | Galaxy S9 | $699.00 |
        """
        full_text = self.extract_pdf_text(pdf_path)
        missing = []
        for item in expected_strings:
            if str(item) not in full_text:
                missing.append(str(item))
                
        if missing:
            raise AssertionError(
                f"PDF verification failed for '{pdf_path}'.\n"
                f"Missing expected strings: {missing}\n\n"
                f"Extracted PDF Text:\n{full_text}"
            )
        print(f"[OK] Verified strings in PDF: {list(expected_strings)}")
