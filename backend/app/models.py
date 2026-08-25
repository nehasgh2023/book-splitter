from pydantic import BaseModel
from typing import List, Optional

class BookMetadata(BaseModel):
    book_title: str
    author: Optional[str] = None
    total_pages: int
    chapters: List[str]
    detection_method: str  # "bookmarks" or "heuristic"

class SplitRequest(BaseModel):
    file_path: str
    chapters: List[str]
    save_location: str  # "local" or "google_drive"
    book_name: str

class GoogleDriveUploadResponse(BaseModel):
    folder_id: str
    folder_url: str
    files_uploaded: int
    message: str
