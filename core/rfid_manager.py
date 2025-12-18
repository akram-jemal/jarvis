"""
RFID code resolution and book mapping.
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any
from config.settings import RFID_MAPPING_FILE
from utils.logger import get_logger

logger = get_logger()


def load_rfid_mapping() -> Dict[str, Dict[str, Any]]:
    """
    Load RFID to book mapping from JSON file.
    
    Returns:
        Dictionary mapping RFID codes to book metadata
        
    Raises:
        FileNotFoundError: If mapping file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    if not RFID_MAPPING_FILE.exists():
        logger.error(f"RFID mapping file not found: {RFID_MAPPING_FILE}")
        raise FileNotFoundError(f"RFID mapping file not found: {RFID_MAPPING_FILE}")
    
    with open(RFID_MAPPING_FILE, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    
    logger.info(f"Loaded RFID mapping with {len(mapping)} books")
    return mapping


def resolve_rfid(rfid_code: str) -> Optional[Dict[str, Any]]:
    """
    Resolve RFID code to book metadata.
    
    Args:
        rfid_code: RFID code to resolve
        
    Returns:
        Dictionary with 'title' and 'pdf_path', or None if not found
    """
    try:
        mapping = load_rfid_mapping()
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load RFID mapping: {e}")
        return None
    
    # Normalize RFID code
    normalized_code = rfid_code.strip().upper()
    
    if normalized_code not in mapping:
        logger.warning(f"RFID code not found: {rfid_code}")
        return None
    
    book_info = mapping[normalized_code].copy()
    
    # Convert path string to Path object
    pdf_path = Path(book_info['pdf_path'])
    
    # If path is relative, make it relative to project root
    if not pdf_path.is_absolute():
        pdf_path = Path(__file__).parent.parent / pdf_path
    
    # Check if PDF file exists
    if not pdf_path.exists():
        logger.error(f"PDF file not found: {pdf_path}")
        return None
    
    book_info['pdf_path'] = pdf_path
    logger.info(f"Resolved RFID {rfid_code} to book: {book_info['title']}")
    
    return book_info

