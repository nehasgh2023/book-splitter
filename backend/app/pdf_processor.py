import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import PyPDF2
import pdfplumber

class PDFProcessor:
    """Handle PDF processing including metadata extraction and chapter detection"""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.pdf_reader = None
        self.total_pages = 0
        self._load_pdf()

    def _load_pdf(self):
        """Load PDF file"""
        with open(self.pdf_path, 'rb') as file:
            self.pdf_reader = PyPDF2.PdfReader(file)
            self.total_pages = len(self.pdf_reader.pages)

    def get_metadata(self) -> Dict:
        """Extract metadata from PDF"""
        metadata = self.pdf_reader.metadata

        author = None
        if metadata:
            author = metadata.get('/Author', None)
            if author:
                author = author.strip() if isinstance(author, str) else str(author)

        title = None
        if metadata:
            title = metadata.get('/Title', None)
            if title:
                title = title.strip() if isinstance(title, str) else str(title)

        return {
            "author": author or "Unknown",
            "title": title or "Untitled",
            "total_pages": self.total_pages
        }

    def extract_chapters(self) -> Tuple[List[str], str]:
        """
        Extract chapters from PDF.
        Returns tuple of (chapter_list, detection_method)
        """
        # Try bookmark extraction first
        chapters = self._extract_from_bookmarks()
        if chapters:
            return chapters, "bookmarks"

        # Fallback to heuristic detection
        chapters = self._detect_chapters_by_text()
        if chapters:
            return chapters, "heuristic"

        # If no chapters detected, return default chapters
        return self._generate_default_chapters(), "default"

    def _extract_from_bookmarks(self) -> List[str]:
        """Extract chapter names from PDF bookmarks/outline"""
        chapters = []
        try:
            if self.pdf_reader.outline:
                for item in self.pdf_reader.outline:
                    if isinstance(item, str):
                        chapters.append(item.strip())
                    elif hasattr(item, 'title'):
                        chapters.append(item.title.strip())
            return chapters
        except Exception as e:
            print(f"Error extracting bookmarks: {e}")
            return []

    def _detect_chapters_by_text(self) -> List[str]:
        """Detect chapters by scanning text for chapter patterns"""
        chapters = []
        chapter_pattern = r'(?:^|\n)\s*(chapter\s+\d+|chapter:.*?|introduction|part\s+\d+|appendix.*?)\s*$'

        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages[:min(50, len(pdf.pages))]:  # Scan first 50 pages
                    text = page.extract_text()
                    if text:
                        matches = re.findall(chapter_pattern, text, re.IGNORECASE | re.MULTILINE)
                        chapters.extend([m.strip() for m in matches])

            # Remove duplicates while preserving order
            seen = set()
            unique_chapters = []
            for ch in chapters:
                if ch.lower() not in seen:
                    seen.add(ch.lower())
                    unique_chapters.append(ch)

            return unique_chapters
        except Exception as e:
            print(f"Error detecting chapters by text: {e}")
            return []

    def _generate_default_chapters(self) -> List[str]:
        """Generate default chapter names based on page count"""
        # Simple default: create chapters of ~30 pages each
        chapters_per_section = max(30, self.total_pages // 5)
        chapters = []
        chapter_num = 1

        for i in range(0, self.total_pages, chapters_per_section):
            chapters.append(f"Chapter {chapter_num}")
            chapter_num += 1

        return chapters if chapters else ["Full Book"]

    def split_pdf_by_chapters(self, chapters: List[str], output_dir: str) -> bool:
        """
        Split PDF by chapters and save to output directory

        Args:
            chapters: List of chapter names
            output_dir: Directory to save split PDFs

        Returns:
            bool: Success status
        """
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            pages_per_chapter = max(1, self.total_pages // len(chapters))

            with open(self.pdf_path, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)

                for i, chapter_name in enumerate(chapters):
                    writer = PyPDF2.PdfWriter()

                    # Calculate page range for this chapter
                    start_page = i * pages_per_chapter
                    end_page = (i + 1) * pages_per_chapter if i < len(chapters) - 1 else len(reader.pages)

                    # Add pages to writer
                    for page_num in range(start_page, min(end_page, len(reader.pages))):
                        writer.add_page(reader.pages[page_num])

                    # Generate filename
                    safe_chapter_name = self._sanitize_filename(chapter_name)
                    output_path = os.path.join(output_dir, f"{i+1:02d}_{safe_chapter_name}.pdf")

                    # Write PDF
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)

            return True
        except Exception as e:
            print(f"Error splitting PDF: {e}")
            return False

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Remove invalid characters from filename"""
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        # Remove multiple underscores
        filename = re.sub(r'_+', '_', filename)
        # Limit length
        return filename[:100]
