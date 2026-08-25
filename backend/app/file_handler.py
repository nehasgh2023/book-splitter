import os
import shutil
from pathlib import Path
from typing import Tuple, Optional
import aiofiles

class FileHandler:
    """Handle file operations for PDF uploads"""

    ALLOWED_EXTENSIONS = {'pdf'}
    MAX_FILE_SIZE = 524288000  # 500MB

    @staticmethod
    def get_upload_dir() -> str:
        """Get or create uploads directory"""
        upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
        Path(upload_dir).mkdir(parents=True, exist_ok=True)
        return upload_dir

    @staticmethod
    def validate_file(filename: str, file_size: int) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file

        Returns: (is_valid, error_message)
        """
        if not filename:
            return False, "No filename provided"

        # Check extension
        if '.' not in filename or filename.rsplit('.', 1)[1].lower() not in FileHandler.ALLOWED_EXTENSIONS:
            return False, "File must be a PDF"

        # Check file size
        if file_size > FileHandler.MAX_FILE_SIZE:
            return False, f"File size exceeds maximum {FileHandler.MAX_FILE_SIZE / (1024*1024):.0f}MB"

        if file_size == 0:
            return False, "File is empty"

        return True, None

    @staticmethod
    async def save_upload(filename: str, file_content: bytes) -> Tuple[bool, str]:
        """
        Save uploaded file to disk

        Returns: (success, file_path_or_error)
        """
        try:
            # Validate
            is_valid, error = FileHandler.validate_file(filename, len(file_content))
            if not is_valid:
                return False, error

            # Create safe filename
            safe_filename = FileHandler._sanitize_filename(filename)
            upload_dir = FileHandler.get_upload_dir()
            file_path = os.path.join(upload_dir, safe_filename)

            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)

            return True, file_path

        except Exception as e:
            return False, f"Error saving file: {str(e)}"

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Remove potentially dangerous characters from filename"""
        import re
        # Remove path separators and special characters
        filename = os.path.basename(filename)
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        return filename if filename else "upload.pdf"

    @staticmethod
    def delete_temp_file(file_path: str) -> bool:
        """Delete temporary file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            return False

    @staticmethod
    def cleanup_old_uploads(max_age_hours: int = 24) -> int:
        """
        Clean up old uploaded files

        Returns: Number of files deleted
        """
        import time
        upload_dir = FileHandler.get_upload_dir()
        deleted_count = 0

        try:
            current_time = time.time()
            for filename in os.listdir(upload_dir):
                file_path = os.path.join(upload_dir, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > (max_age_hours * 3600):
                        FileHandler.delete_temp_file(file_path)
                        deleted_count += 1
        except Exception as e:
            print(f"Error cleaning up uploads: {e}")

        return deleted_count
