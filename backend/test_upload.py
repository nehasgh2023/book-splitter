#!/usr/bin/env python
"""Test the PDF upload endpoint"""

import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

async def test_upload():
    """Test PDF upload with local file"""
    from app.file_handler import FileHandler
    from app.pdf_processor import PDFProcessor

    test_pdf_path = os.path.join(os.path.dirname(__file__), 'test_sample.pdf')

    print(f"[TEST] Testing PDF upload functionality")
    print(f"[INFO] Test PDF path: {test_pdf_path}")
    print(f"[INFO] File exists: {os.path.exists(test_pdf_path)}")
    print(f"[INFO] File size: {os.path.getsize(test_pdf_path)} bytes")

    # Test 1: File validation
    print(f"\n[TEST 1] File validation")
    file_size = os.path.getsize(test_pdf_path)
    is_valid, error = FileHandler.validate_file("test_sample.pdf", file_size)
    print(f"  Valid: {is_valid}")
    if error:
        print(f"  Error: {error}")
    else:
        print(f"  [PASS] File validation passed")

    # Test 2: Save upload
    print(f"\n[TEST 2] File save")
    with open(test_pdf_path, 'rb') as f:
        content = f.read()

    success, result = await FileHandler.save_upload("test_sample.pdf", content)
    print(f"  Success: {success}")
    if success:
        print(f"  [PASS] File saved to: {result}")
        saved_path = result
    else:
        print(f"  [FAIL] Error: {result}")
        return

    # Test 3: PDF Processing
    print(f"\n[TEST 3] PDF processing")
    try:
        processor = PDFProcessor(saved_path)
        metadata = processor.get_metadata()
        print(f"  [PASS] Metadata extracted:")
        print(f"    - Title: {metadata['title']}")
        print(f"    - Author: {metadata['author']}")
        print(f"    - Pages: {metadata['total_pages']}")

        chapters, detection = processor.extract_chapters()
        print(f"  [PASS] Chapters detected:")
        print(f"    - Method: {detection}")
        print(f"    - Count: {len(chapters)}")
        print(f"    - Chapters: {chapters}")

    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return

    print(f"\n[SUMMARY] All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_upload())
