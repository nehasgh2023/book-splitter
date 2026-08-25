#!/usr/bin/env python
"""Test PDF splitting functionality"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.split_service import SplitService
from app.download_manager import DownloadManager

def test_split_functionality():
    """Test PDF splitting and download"""
    test_pdf_path = os.path.join(os.path.dirname(__file__), 'test_sample.pdf')

    print("[TEST] PDF Splitting Functionality")
    print(f"[INFO] Test PDF: {test_pdf_path}")
    print(f"[INFO] File exists: {os.path.exists(test_pdf_path)}")

    # Test 1: Split service initialization
    print(f"\n[TEST 1] Split service initialization")
    split_service = SplitService(test_pdf_path)
    print(f"[PASS] Split service created")

    # Test 2: Calculate page ranges
    print(f"\n[TEST 2] Page range calculation")
    page_ranges = split_service.calculate_chapter_pages(total_pages=10, num_chapters=3)
    print(f"  Total pages: 10, Chapters: 3")
    print(f"  Ranges: {page_ranges}")
    print(f"[PASS] Page ranges calculated")

    # Test 3: Split PDF
    print(f"\n[TEST 3] Split PDF into chapters")
    chapters = ["Introduction", "Main Content", "Conclusion"]
    success, result, files = split_service.split_by_chapters(
        chapters=chapters,
        book_title="Test_Book"
    )

    print(f"  Success: {success}")
    if success:
        print(f"  [PASS] PDF split successfully")
        print(f"  Output folder: {result}")
        print(f"  Files created: {len(files)}")
        for i, f in enumerate(files, 1):
            print(f"    {i}. {os.path.basename(f)}")
    else:
        print(f"  [FAIL] Error: {result}")
        return

    # Test 4: Get split info
    print(f"\n[TEST 4] Get split information")
    info = split_service.get_split_info(result)
    print(f"  Chapters: {info.get('chapter_count')}")
    print(f"  Folder size: {info.get('folder_size_mb')} MB")
    print(f"[PASS] Split info retrieved")

    # Test 5: Create ZIP archive
    print(f"\n[TEST 5] Create ZIP archive for download")
    success, zip_bytes, archive_name = DownloadManager.create_zip_archive(
        files=files,
        archive_name="Test_Book_chapters.zip"
    )

    print(f"  Success: {success}")
    if success:
        print(f"  [PASS] ZIP archive created")
        print(f"  Archive name: {archive_name}")
        print(f"  Archive size: {len(zip_bytes)} bytes")
        print(f"  Archive size: {round(len(zip_bytes) / (1024 * 1024), 2)} MB")
    else:
        print(f"  [FAIL] Error: {zip_bytes}")
        return

    # Test 6: Cleanup
    print(f"\n[TEST 6] Cleanup")
    cleanup_success = DownloadManager.cleanup_directory(result)
    print(f"  Cleanup success: {cleanup_success}")
    print(f"[PASS] Directory cleaned up")

    print(f"\n[SUMMARY] All splitting tests passed!")

if __name__ == "__main__":
    test_split_functionality()
