"""
Helper utility functions.
"""
import re
from typing import List, Tuple, Optional


def normalize_rfid_code(code: str) -> str:
    """
    Normalize RFID code input (trim, uppercase).
    
    Args:
        code: Raw RFID code input
        
    Returns:
        Normalized RFID code
    """
    return code.strip().upper()


def find_all_chapters(text: str) -> List[Tuple[int, int, str]]:
    """
    Find all chapter markers in text.
    
    Args:
        text: Text to search
        
    Returns:
        List of tuples: (position, chapter_number, chapter_title)
    """
    chapters = []
    
    # Pattern 1: "Chapter 1", "Chapter One", "CHAPTER 1", etc.
    pattern1 = re.compile(
        r'(?i)^\s*(Chapter\s+(?:[IVX]+|\d+|[A-Z]+|One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten))\s*:?\s*(.*?)$',
        re.MULTILINE
    )
    for match in pattern1.finditer(text):
        chapters.append((match.start(), -1, match.group(0).strip()))
    
    # Pattern 2: "1. Title", "1 Title"
    pattern2 = re.compile(r'(?m)^\s*(\d+)\s*\.?\s+(.+?)(?=\n\n|\n\d+\.|\Z)', re.MULTILINE)
    for match in pattern2.finditer(text):
        num_str = match.group(1)
        try:
            num = int(num_str)
            # Only consider if it's likely a chapter (numbered 1-20 typically)
            if 1 <= num <= 20:
                chapters.append((match.start(), num, match.group(0).strip()))
        except ValueError:
            pass
    
    # Pattern 3: Roman numerals "I.", "II.", "III.", etc.
    roman_pattern = re.compile(r'(?m)^\s*([IVX]+)\s*\.?\s+(.+?)(?=\n\n|\n[IVX]+\.|\Z)', re.MULTILINE)
    roman_to_int = {
        'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
        'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
        'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15,
        'XVI': 16, 'XVII': 17, 'XVIII': 18, 'XIX': 19, 'XX': 20
    }
    for match in roman_pattern.finditer(text):
        roman = match.group(1).upper()
        if roman in roman_to_int:
            chapters.append((match.start(), roman_to_int[roman], match.group(0).strip()))
    
    # Sort by position
    chapters.sort(key=lambda x: x[0])
    
    return chapters


def clean_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    # Replace multiple newlines with double newline (paragraph break)
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    return text.strip()


def extract_context_around_position(text: str, position: int, context_size: int = 2000) -> str:
    """
    Extract text context around a given position.
    
    Args:
        text: Full text
        position: Central position
        context_size: Total context size in characters
        
    Returns:
        Context text
    """
    half_size = context_size // 2
    start = max(0, position - half_size)
    end = min(len(text), position + half_size)
    
    # Try to start/end at word boundaries
    if start > 0:
        start = text.rfind(' ', start - 100, start) + 1
    if end < len(text):
        end = text.find(' ', end, end + 100)
        if end == -1:
            end = len(text)
    
    return text[start:end].strip()

