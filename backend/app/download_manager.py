import os
import zipfile
import io
from pathlib import Path
from typing import Tuple, Optional

class DownloadManager:
    """Manage PDF file downloads and ZIP creation"""

    @staticmethod
    def create_zip_archive(
        files: list,
        archive_name: str = "chapters.zip"
    ) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """
        Create a ZIP archive of PDF files

        Args:
            files: List of file paths to include
            archive_name: Name for the ZIP file

        Returns:
            (success, zip_bytes_or_error, archive_name)
        """
        try:
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_path in files:
                    if os.path.exists(file_path):
                        # Use just the filename in the archive
                        arcname = os.path.basename(file_path)
                        zip_file.write(file_path, arcname=arcname)

            zip_bytes = zip_buffer.getvalue()

            if len(zip_bytes) == 0:
                return False, "No files added to archive", None

            return True, zip_bytes, archive_name

        except Exception as e:
            return False, f"Error creating ZIP: {str(e)}", None

    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """Get file information"""
        try:
            if not os.path.exists(file_path):
                return {"error": "File not found"}

            stat = os.stat(file_path)
            return {
                "path": file_path,
                "filename": os.path.basename(file_path),
                "size": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def read_file_bytes(file_path: str) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """Read file and return as bytes"""
        try:
            if not os.path.exists(file_path):
                return False, None, "File not found"

            with open(file_path, 'rb') as f:
                file_bytes = f.read()

            return True, file_bytes, None

        except Exception as e:
            return False, None, str(e)

    @staticmethod
    def cleanup_file(file_path: str) -> bool:
        """Delete a file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            return False

    @staticmethod
    def cleanup_directory(directory_path: str) -> bool:
        """Delete a directory and all contents"""
        try:
            import shutil
            if os.path.exists(directory_path):
                shutil.rmtree(directory_path)
            return True
        except Exception as e:
            print(f"Error deleting directory {directory_path}: {e}")
            return False
