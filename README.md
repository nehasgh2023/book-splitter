# PDF Book Learning App

A web application that allows users to upload PDF books, extract metadata (author, title, chapter count, page count), and split books into individual chapter PDFs. Chapters can be saved to either the local computer or Google Drive.

## Features

- 📚 Upload PDF books with drag-and-drop interface
- 📖 Extract book metadata (author, title, pages, chapters)
- 🔀 Automatically detect and split books by chapters
- 💾 Save chapters locally or upload to Google Drive
- 📁 Organized folder structure for chapter storage
- 🔐 Secure OAuth2 integration with Google Drive

## Tech Stack

### Frontend
- React 18+
- Axios
- Material-UI / Shadcn UI
- pdfjs-dist

### Backend
- Python 3.8+
- FastAPI
- PyPDF2
- pdfplumber
- Google Drive API

## Project Structure

```
pdf-book-learning-app/
├── frontend/                 # React web application
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── .env.example
├── backend/                  # Python FastAPI server
│   ├── app/
│   ├── requirements.txt
│   ├── .env.example
│   └── main.py
├── docs/                     # Documentation
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites
- Node.js v18+ (for frontend)
- Python 3.8+ (for backend)
- Git
- Google Cloud Project (optional, for Google Drive integration)

### Setup Instructions

#### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/pdf-book-learning-app.git
cd pdf-book-learning-app
```

#### 2. Backend Setup
```bash
cd backend
python -m venv venv

# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

#### 3. Frontend Setup
```bash
cd frontend
npm install
```

#### 4. Environment Variables
Create `.env` files in both frontend and backend directories using `.env.example` as a template.

#### 5. Run the Application
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
npm start
```

Visit `http://localhost:3000` in your browser.

## API Endpoints

### POST `/api/upload`
Upload a PDF file and extract metadata.

**Request**: Multipart form data with `file` field
**Response**:
```json
{
  "book_title": "string",
  "author": "string",
  "total_pages": "number",
  "chapters": ["Chapter 1", "Chapter 2", ...],
  "detection_method": "bookmarks|heuristic"
}
```

### POST `/api/split`
Split PDF into chapters and save to local or Google Drive.

**Request**:
```json
{
  "file_path": "string",
  "chapters": ["Chapter 1", ...],
  "save_location": "local|google_drive",
  "book_name": "string"
}
```

**Response**: Success confirmation with download links or Google Drive folder ID.

### POST `/api/auth/google`
Handle Google OAuth2 authentication for Drive access.

## Testing

### Manual Testing Checklist
- [ ] Upload sample PDF and verify metadata extraction
- [ ] Split to local computer and verify chapters download
- [ ] Split to Google Drive and verify folder structure
- [ ] Test with multi-chapter books
- [ ] Verify chapter names match original PDF
- [ ] Test error handling with corrupted PDFs

### Sample Test PDFs
- Use freely available PDFs from Project Gutenberg (e.g., "Pride and Prejudice")
- Create test PDFs with clear chapter markers

## Deployment

### Backend Deployment Options
- Heroku
- AWS Lambda + API Gateway
- DigitalOcean App Platform
- Google Cloud Run

### Frontend Deployment Options
- Vercel (recommended)
- Netlify
- GitHub Pages
- AWS S3 + CloudFront

## Google Drive Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Drive API
4. Create OAuth2 credentials (Desktop application)
5. Download credentials and add to `.env` file

Required scopes:
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/userinfo.profile`

## Contributing

Contributions are welcome! Please follow these steps:
1. Create a feature branch (`git checkout -b feature/your-feature`)
2. Commit changes (`git commit -m 'feat: add your feature'`)
3. Push to branch (`git push origin feature/your-feature`)
4. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Note**: This app requires PDF files with clear structure for optimal chapter detection. PDFs with complex layouts may require manual chapter specification.
