import os
import shutil
from pathlib import Path
from typing import List, Tuple, Dict
from PyPDF2 import PdfReader, PdfWriter

class SplitService:
    """Handle PDF splitting and chapter extraction"""

    def __init__(self, pdf_path: str, output_base_dir: str = None):
        self.pdf_path = pdf_path
        self.output_base_dir = output_base_dir or os.path.join(
            os.path.dirname(__file__), '..', 'splits'
        )
        Path(self.output_base_dir).mkdir(parents=True, exist_ok=True)

    def calculate_chapter_pages(self, total_pages: int, num_chapters: int) -> List[Tuple[int, int]]:
        """
        Calculate page ranges for each chapter

        Returns list of (start_page, end_page) tuples (0-indexed)
        """
        if num_chapters <= 0:
            return [(0, total_pages - 1)]

        if num_chapters > total_pages:
            # One page per chapter
            return [(i, i) for i in range(total_pages)]

        pages_per_chapter = total_pages // num_chapters
        remainder = total_pages % num_chapters

        ranges = []
        start = 0

        for i in range(num_chapters):
            # Distribute extra pages to earlier chapters
            end = start + pages_per_chapter + (1 if i < remainder else 0) - 1
            ranges.append((start, end))
            start = end + 1

        return ranges

    def split_by_chapters(
        self,
        chapters: List[str],
        book_title: str = "Book"
    ) -> Tuple[bool, str, List[str]]:
        """
        Split PDF into chapter files

        Args:
            chapters: List of chapter names
            book_title: Name for the output folder

        Returns:
            (success, folder_path_or_error, list_of_file_paths)
        """
        try:
            # Create output folder
            safe_title = self._sanitize_folder_name(book_title)
            output_folder = os.path.join(self.output_base_dir, safe_title)
            Path(output_folder).mkdir(parents=True, exist_ok=True)

            # Open source PDF
            with open(self.pdf_path, 'rb') as pdf_file:
                reader = PdfReader(pdf_file)
                total_pages = len(reader.pages)

                if total_pages == 0:
                    return False, "PDF has no pages", []

                # Calculate page ranges for chapters
                page_ranges = self.calculate_chapter_pages(total_pages, len(chapters))

                output_files = []

                # Split and save each chapter
                for chapter_idx, (chapter_name, (start_page, end_page)) in enumerate(
                    zip(chapters, page_ranges)
                ):
                    # Create writer for this chapter
                    writer = PdfWriter()

                    # Add pages to this chapter
                    for page_num in range(start_page, min(end_page + 1, total_pages)):
                        writer.add_page(reader.pages[page_num])

                    # Generate safe filename
                    safe_filename = self._sanitize_filename(chapter_name)
                    chapter_num = f"{chapter_idx + 1:02d}"
                    output_filename = f"{chapter_num}_{safe_filename}.pdf"
                    output_path = os.path.join(output_folder, output_filename)

                    # Write PDF file
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)

                    output_files.append(output_path)

                return True, output_folder, output_files

        except Exception as e:
            return False, f"Error splitting PDF: {str(e)}", []

    def get_split_info(self, output_folder: str) -> Dict:
        """Get information about split chapters"""
        try:
            if not os.path.exists(output_folder):
                return {"error": "Folder not found"}

            pdf_files = sorted([f for f in os.listdir(output_folder) if f.endswith('.pdf')])
            total_size = sum(
                os.path.getsize(os.path.join(output_folder, f))
                for f in pdf_files
            )

            return {
                "folder": output_folder,
                "chapter_count": len(pdf_files),
                "chapters": pdf_files,
                "total_size": total_size,
                "folder_size_mb": round(total_size / (1024 * 1024), 2)
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Remove invalid characters from filename"""
        import re
        filename = os.path.basename(filename)
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = filename.replace(' ', '_')
        filename = re.sub(r'_+', '_', filename)
        return filename[:100] if filename else "chapter"

    @staticmethod
    def _sanitize_folder_name(name: str) -> str:
        """Remove invalid characters from folder name"""
        import re
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        name = name.replace(' ', '_')
        name = re.sub(r'_+', '_', name)
        return name[:50] if name else "book"

    def cleanup_old_splits(self, max_age_hours: int = 24) -> int:
        """
        Clean up old split folders

        Returns: Number of folders deleted
        """
        import time
        deleted_count = 0

        try:
            current_time = time.time()
            for folder_name in os.listdir(self.output_base_dir):
                folder_path = os.path.join(self.output_base_dir, folder_name)
                if os.path.isdir(folder_path):
                    folder_age = current_time - os.path.getmtime(folder_path)
                    if folder_age > (max_age_hours * 3600):
                        shutil.rmtree(folder_path)
                        deleted_count += 1
        except Exception as e:
            print(f"Error cleaning up splits: {e}")

        return deleted_count
