"""
File parser module for extracting text from various document formats.
Supports PDF, DOCX, and TXT files.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
import pypdf
from docx import Document
from backend.config import SUPPORTED_EXTENSIONS, DOCUMENTS_DIR


class FileParser:
    """Handles text extraction from various document formats."""
    
    def __init__(self):
        self.supported_extensions = SUPPORTED_EXTENSIONS
    
    def is_supported(self, file_path: str) -> bool:
        """Check if file extension is supported."""
        ext = Path(file_path).suffix.lower()
        return ext in self.supported_extensions
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from DOCX: {str(e)}")
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from TXT: {str(e)}")
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from file based on extension."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not self.is_supported(file_path):
            raise ValueError(f"Unsupported file type: {Path(file_path).suffix}")
        
        ext = Path(file_path).suffix.lower()
        
        if ext == ".pdf":
            return self.extract_text_from_pdf(file_path)
        elif ext == ".docx":
            return self.extract_text_from_docx(file_path)
        elif ext == ".txt":
            return self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def save_uploaded_file(self, uploaded_file, filename: str) -> str:
        """Save uploaded file to documents directory."""
        file_path = DOCUMENTS_DIR / filename
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return str(file_path)
    
    def get_file_metadata(self, file_path: str) -> Dict:
        """Get metadata about the file."""
        path = Path(file_path)
        return {
            "filename": path.name,
            "size": os.path.getsize(file_path),
            "extension": path.suffix.lower(),
            "path": str(file_path)
        }

