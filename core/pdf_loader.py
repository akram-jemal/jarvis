"""
PDF text extraction using pdfplumber.
"""
import pdfplumber
from pathlib import Path
from typing import Optional
from utils.logger import get_logger
from utils.helpers import clean_whitespace

logger = get_logger()


def load_pdf(pdf_path: Path) -> Optional[str]:
    """
    Extract text from PDF file.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text, or None on failure
    """
    if not pdf_path.exists():
        logger.error(f"PDF file not found: {pdf_path}")
        return None
    
    try:
        text_parts = []
        
        with pdfplumber.open(pdf_path) as pdf:
            logger.info(f"Extracting text from PDF: {pdf_path} ({len(pdf.pages)} pages)")
            
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num}: {e}")
                    continue
        
        full_text = '\n\n'.join(text_parts)
        
        if not full_text or len(full_text.strip()) < 100:
            logger.warning("Extracted text is too short or empty")
            return None
        
        # Clean the text
        cleaned_text = clean_text(full_text)
        
        logger.info(f"Successfully extracted {len(cleaned_text)} characters from PDF")
        return cleaned_text
        
    except Exception as e:
        logger.error(f"Failed to load PDF: {e}")
        return None


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text.
    
    Args:
        text: Raw extracted text
        
    Returns:
        Cleaned text
    """
    # Remove excessive whitespace
    text = clean_whitespace(text)
    
    # Remove common header/footer patterns (page numbers, etc.)
    # Remove lines that are just numbers (likely page numbers)
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        # Skip lines that are just page numbers or very short repeated text
        if stripped.isdigit() and len(stripped) <= 3:
            continue
        # Skip very short lines that appear frequently (likely headers/footers)
        if len(stripped) < 3:
            continue
        cleaned_lines.append(line)
    
    text = '\n'.join(cleaned_lines)
    
    # Normalize whitespace again
    text = clean_whitespace(text)
    
    return text

