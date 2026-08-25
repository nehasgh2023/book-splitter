#!/usr/bin/env python
"""Create a test PDF file for testing"""

from PyPDF2 import PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os

def create_test_pdf():
    """Create a test PDF with book content"""
    output_path = os.path.join(os.path.dirname(__file__), "test_book.pdf")

    # Create PDF with reportlab
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)

    # Add pages with chapter content
    chapters = [
        ("Chapter 1: Introduction", "This is the introduction chapter with some content..."),
        ("Chapter 2: Getting Started", "This chapter covers the basics..."),
        ("Chapter 3: Advanced Topics", "Advanced topics and techniques..."),
    ]

    for chapter_num, (chapter_title, content) in enumerate(chapters, 1):
        # Add chapter title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, chapter_title)

        # Add chapter content
        c.setFont("Helvetica", 12)
        c.drawString(50, 700, content)

        # Add some spacing
        for i in range(20):
            c.drawString(50, 650 - (i * 30), f"Line {i + 1} of chapter {chapter_num}")

        c.showPage()

    c.save()
    pdf_buffer.seek(0)

    # Write to file
    with open(output_path, 'wb') as f:
        f.write(pdf_buffer.getvalue())

    print(f"Test PDF created: {output_path}")
    return output_path

if __name__ == "__main__":
    create_test_pdf()
