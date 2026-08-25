from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import List
import os

from app.pdf_processor import PDFProcessor
from app.file_handler import FileHandler
from app.models import BookMetadata

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

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "PDF Learning App Backend is running"}

@router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "PDF Book Learning App API", "docs": "/docs"}
