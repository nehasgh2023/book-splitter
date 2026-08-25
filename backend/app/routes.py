from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from typing import List
import os
import io

from app.pdf_processor import PDFProcessor
from app.file_handler import FileHandler
from app.split_service import SplitService
from app.download_manager import DownloadManager
from app.models import BookMetadata, SplitRequest

router = APIRouter(prefix="/api", tags=["PDF Processing"])

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)) -> dict:
    """
    Upload a PDF file and extract metadata

    Returns:
        - book_title: Extracted or default book title
        - author: Author name from metadata
        - total_pages: Total number of pages
        - chapters: List of detected chapter names
        - detection_method: How chapters were detected (bookmarks/heuristic/default)
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    try:
        # Read file content
        file_content = await file.read()

        # Validate and save file
        success, result = await FileHandler.save_upload(file.filename, file_content)
        if not success:
            raise HTTPException(status_code=400, detail=result)

        file_path = result

        # Process PDF
        processor = PDFProcessor(file_path)
        metadata = processor.get_metadata()
        chapters, detection_method = processor.extract_chapters()

        # Prepare response
        response = {
            "book_title": metadata["title"],
            "author": metadata["author"],
            "total_pages": metadata["total_pages"],
            "chapters": chapters,
            "detection_method": detection_method,
            "file_path": file_path,
            "file_size": len(file_content),
            "chapter_count": len(chapters)
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        # Clean up file if error occurs
        if 'file_path' in locals():
            FileHandler.delete_temp_file(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@router.post("/split")
async def split_pdf(request: SplitRequest) -> dict:
    """
    Split a PDF into chapters and prepare for download

    Request body:
        - file_path: Path to the uploaded PDF file
        - chapters: List of chapter names (order matters)
        - save_location: "local" for ZIP download, "google_drive" for cloud storage
        - book_name: Name for the output folder

    Returns:
        - success: Whether split was successful
        - folder_path: Path to the folder containing split chapters
        - chapters: List of created chapter filenames
        - download_url: URL for downloading the ZIP file (local only)
        - message: Status message
    """
    try:
        # Validate file exists
        if not os.path.exists(request.file_path):
            raise HTTPException(status_code=400, detail="PDF file not found. Re-upload the PDF.")

        # Validate request
        if not request.chapters or len(request.chapters) == 0:
            raise HTTPException(status_code=400, detail="At least one chapter name required")

        if not request.book_name:
            raise HTTPException(status_code=400, detail="Book name required")

        # Split PDF
        split_service = SplitService(request.file_path)
        success, result, file_paths = split_service.split_by_chapters(
            chapters=request.chapters,
            book_title=request.book_name
        )

        if not success:
            raise HTTPException(status_code=500, detail=result)

        # Get folder info
        folder_info = split_service.get_split_info(result)

        # Prepare response based on save location
        response = {
            "success": True,
            "folder_path": result,
            "chapters": folder_info.get("chapters", []),
            "chapter_count": folder_info.get("chapter_count", 0),
            "total_size": folder_info.get("total_size", 0),
            "save_location": request.save_location,
            "message": f"PDF split into {folder_info.get('chapter_count', 0)} chapters"
        }

        # For local storage, prepare download
        if request.save_location == "local":
            success, zip_bytes, archive_name = DownloadManager.create_zip_archive(
                files=file_paths,
                archive_name=f"{request.book_name}_chapters.zip"
            )

            if success:
                response["download_ready"] = True
                response["archive_name"] = archive_name
                response["archive_size"] = len(zip_bytes)
                response["archive_size_mb"] = round(len(zip_bytes) / (1024 * 1024), 2)
            else:
                response["download_ready"] = False
                response["download_error"] = zip_bytes  # zip_bytes is error message here

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error splitting PDF: {str(e)}")

@router.get("/download/{book_name}")
async def download_chapters(book_name: str):
    """
    Download split chapters as ZIP file

    Args:
        book_name: Name of the book (folder name)

    Returns:
        ZIP file with all chapter PDFs
    """
    try:
        split_service = SplitService()
        folder_path = os.path.join(split_service.output_base_dir, book_name)

        if not os.path.exists(folder_path):
            raise HTTPException(status_code=404, detail="Chapter folder not found")

        # Get all PDF files
        pdf_files = [
            os.path.join(folder_path, f)
            for f in sorted(os.listdir(folder_path))
            if f.endswith('.pdf')
        ]

        if not pdf_files:
            raise HTTPException(status_code=404, detail="No chapter files found")

        # Create ZIP
        success, zip_bytes, archive_name = DownloadManager.create_zip_archive(
            files=pdf_files,
            archive_name=f"{book_name}_chapters.zip"
        )

        if not success:
            raise HTTPException(status_code=500, detail=zip_bytes)

        # Return as downloadable file
        return StreamingResponse(
            iter([zip_bytes]),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={archive_name}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading chapters: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "PDF Learning App Backend is running"}

@router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "PDF Book Learning App API", "docs": "/docs"}
