import os
import PyPDF2
import fitz  # PyMuPDF
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class PDFProcessor:
    """Class for extracting and processing text from PDF files."""
    
    def __init__(self, pdf_path: Path):
        """Initialize with path to PDF file.
        
        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.extracted_text = ""
        self.pages = []
        self.toc = []
    
    def extract_text(self) -> Dict:
        """Extract text from PDF file with structure preservation.
        
        Returns:
            Dict containing extracted text with structural information
        """
        # Try PyMuPDF (fitz) first as it generally has better structure preservation
        try:
            return self._extract_with_pymupdf()
        except Exception as e:
            print(f"PyMuPDF extraction failed: {e}. Falling back to PyPDF2.")
            return self._extract_with_pypdf2()
    
    def _extract_with_pymupdf(self) -> Dict:
        """Extract text using PyMuPDF (better structure preservation)."""
        result = {
            "metadata": {},
            "toc": [],
            "pages": []
        }
        
        # Open the PDF
        doc = fitz.open(self.pdf_path)
        
        # Extract metadata
        result["metadata"] = {
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
            "keywords": doc.metadata.get("keywords", ""),
            "page_count": len(doc)
        }
        
        # Extract table of contents if available
        toc = doc.get_toc()
        result["toc"] = [{
            "level": t[0],
            "title": t[1],
            "page": t[2]
        } for t in toc]
        
        # Extract text from each page with formatting information
        for page_num, page in enumerate(doc):
            # Get plain text
            text = page.get_text()
            
            # Get blocks which may contain structural information
            blocks = page.get_text("blocks")
            
            # Extract font information to identify headings
            font_info = []
            for block in blocks:
                if len(block) >= 5:  # Block format: (x0, y0, x1, y1, text, block_no, block_type)
                    font_info.append({
                        "text": block[4],
                        "size": block[5] if len(block) > 5 else None,
                        "font": block[6] if len(block) > 6 else None
                    })
            
            result["pages"].append({
                "page_num": page_num + 1,
                "text": text,
                "blocks": blocks,
                "font_info": font_info
            })
        
        # Store the full text
        self.extracted_text = "\n\n".join([page["text"] for page in result["pages"]])
        
        # Close the document
        doc.close()
        
        return result
    
    def _extract_with_pypdf2(self) -> Dict:
        """Extract text using PyPDF2 (fallback method)."""
        result = {
            "metadata": {},
            "toc": [],
            "pages": []
        }
        
        # Open the PDF
        with open(self.pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            
            # Extract metadata
            info = reader.metadata
            if info:
                result["metadata"] = {
                    "title": info.get("/Title", ""),
                    "author": info.get("/Author", ""),
                    "subject": info.get("/Subject", ""),
                    "keywords": info.get("/Keywords", ""),
                    "page_count": len(reader.pages)
                }
            
            # Extract text from each page
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                
                result["pages"].append({
                    "page_num": page_num + 1,
                    "text": text
                })
        
        # Store the full text
        self.extracted_text = "\n\n".join([page["text"] for page in result["pages"]])
        
        return result
    
    def get_chapter_boundaries(self, extracted_data: Dict) -> List[Dict]:
        """Identify chapter boundaries based on TOC and text analysis.
        
        Args:
            extracted_data: Dictionary containing extracted PDF data
            
        Returns:
            List of dictionaries with chapter information
        """
        chapters = []
        
        # If we have a table of contents, use it to identify chapters
        if extracted_data["toc"]:
            for item in extracted_data["toc"]:
                # Consider level 1 items as chapters
                if item["level"] == 1 and "chapter" in item["title"].lower():
                    chapters.append({
                        "title": item["title"],
                        "start_page": item["page"],
                        "end_page": None  # Will be filled in later
                    })
            
            # Set end pages
            for i in range(len(chapters) - 1):
                chapters[i]["end_page"] = chapters[i + 1]["start_page"] - 1
            
            # Set the end page of the last chapter
            if chapters:
                chapters[-1]["end_page"] = extracted_data["metadata"]["page_count"]
        
        # If no TOC or no chapters found, try to identify chapters from text
        if not chapters:
            chapter_pattern = re.compile(r"chapter\s+\d+[\s:]+([^\n]+)", re.IGNORECASE)
            
            for page in extracted_data["pages"]:
                matches = chapter_pattern.findall(page["text"])
                if matches:
                    for match in matches:
                        chapters.append({
                            "title": f"Chapter: {match.strip()}",
                            "start_page": page["page_num"],
                            "end_page": None  # Will be filled in later
                        })
            
            # Set end pages
            for i in range(len(chapters) - 1):
                chapters[i]["end_page"] = chapters[i + 1]["start_page"] - 1
            
            # Set the end page of the last chapter
            if chapters:
                chapters[-1]["end_page"] = extracted_data["metadata"]["page_count"]
        
        return chapters
    
    def extract_chapter_text(self, extracted_data: Dict, chapter_info: Dict) -> str:
        """Extract text for a specific chapter.
        
        Args:
            extracted_data: Dictionary containing extracted PDF data
            chapter_info: Dictionary with chapter boundary information
            
        Returns:
            String containing the chapter text
        """
        chapter_text = ""
        
        start_page = chapter_info["start_page"]
        end_page = chapter_info["end_page"]
        
        for page in extracted_data["pages"]:
            if start_page <= page["page_num"] <= end_page:
                chapter_text += page["text"] + "\n\n"
        
        return chapter_text.strip()