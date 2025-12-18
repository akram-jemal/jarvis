"""
Chapter detection logic to find Chapter 1 and skip front matter.
"""
import re
from typing import Optional
from utils.logger import get_logger
from utils.helpers import find_all_chapters
from config.settings import MIN_FRONT_MATTER_SKIP, MAX_FRONT_MATTER_SKIP

logger = get_logger()


def find_chapter_one_start(text: str) -> int:
    """
    Find the starting position of Chapter 1 in the text.
    
    Args:
        text: Full book text
        
    Returns:
        Character index where Chapter 1 begins
    """
    if not text or len(text) < 100:
        logger.warning("Text is too short to detect chapters")
        return 0
    
    # First, try to find explicit chapter markers
    chapter_position = _find_explicit_chapter_one(text)
    if chapter_position is not None:
        logger.info(f"Found explicit Chapter 1 at position {chapter_position}")
        return chapter_position
    
    # If no explicit chapter found, try to skip front matter
    chapter_position = _skip_front_matter(text)
    if chapter_position is not None:
        logger.info(f"Starting after front matter at position {chapter_position}")
        return chapter_position
    
    # Fallback: skip first portion of document
    fallback_position = int(len(text) * MIN_FRONT_MATTER_SKIP)
    logger.warning(f"Could not detect Chapter 1, using fallback position: {fallback_position}")
    return fallback_position


def _find_explicit_chapter_one(text: str) -> Optional[int]:
    """
    Search for explicit Chapter 1 markers.
    
    Args:
        text: Full text
        
    Returns:
        Position of Chapter 1, or None if not found
    """
    # Pattern 1: "Chapter 1", "Chapter One", "CHAPTER 1", etc.
    patterns = [
        r'(?i)^\s*Chapter\s+1\s*:?\s',
        r'(?i)^\s*Chapter\s+One\s*:?\s',
        r'(?i)^\s*CHAPTER\s+1\s*:?\s',
        r'(?i)^\s*CHAPTER\s+ONE\s*:?\s',
        r'(?i)^\s*Chapter\s+I\s*:?\s',  # Roman numeral I
        r'^\s*1\.\s+[A-Z]',  # "1. Title" at start of line
        r'^\s*I\.\s+[A-Z]',  # "I. Title" at start of line
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            pos = match.start()
            # Verify it's not in the very beginning (likely title page)
            if pos > len(text) * 0.05:  # At least 5% into document
                return pos
    
    # Also check for numbered chapters (1., 2., etc.)
    numbered_chapter = re.search(r'(?m)^\s*1\.\s+(?![0-9])', text)
    if numbered_chapter:
        pos = numbered_chapter.start()
        if pos > len(text) * 0.05:
            return pos
    
    return None


def _skip_front_matter(text: str) -> Optional[int]:
    """
    Skip front matter by finding Table of Contents end or typical front matter sections.
    
    Args:
        text: Full text
        
    Returns:
        Position after front matter, or None if cannot determine
    """
    # Find Table of Contents
    toc_patterns = [
        r'(?i)Table\s+of\s+Contents',
        r'(?i)Contents',
        r'(?i)T\.O\.C\.',
    ]
    
    toc_end = None
    
    for pattern in toc_patterns:
        toc_match = re.search(pattern, text, re.IGNORECASE)
        if toc_match:
            # Find the end of TOC (next chapter marker or section break)
            toc_start = toc_match.start()
            
            # Look for patterns that indicate TOC end:
            # - Multiple line breaks
            # - Page breaks
            # - Next numbered item
            
            # Search for double line breaks after TOC
            toc_section = text[toc_start:toc_start + min(5000, len(text) - toc_start)]
            double_breaks = list(re.finditer(r'\n\s*\n\s*\n', toc_section))
            
            if double_breaks:
                # Take position after last double break in TOC section
                last_break = double_breaks[-1]
                toc_end = toc_start + last_break.end()
                break
    
    if toc_end:
        # Make sure we're not too far into the document
        if toc_end < len(text) * MAX_FRONT_MATTER_SKIP:
            return toc_end
    
    # Try to find common front matter sections and skip past them
    front_matter_keywords = [
        r'(?i)^\s*Copyright',
        r'(?i)^\s*Dedication',
        r'(?i)^\s*Preface',
        r'(?i)^\s*Foreword',
        r'(?i)^\s*Introduction\s*$',  # Introduction as front matter (not "Chapter 1: Introduction")
        r'(?i)^\s*Acknowledgments',
    ]
    
    last_front_matter = 0
    
    for keyword in front_matter_keywords:
        matches = list(re.finditer(keyword, text, re.MULTILINE))
        for match in matches:
            # Only consider if it's in the first 30% of document
            if match.start() < len(text) * MAX_FRONT_MATTER_SKIP:
                # Find end of this section (double line break or next section)
                section_end = _find_section_end(text, match.end())
                if section_end > last_front_matter:
                    last_front_matter = section_end
    
    if last_front_matter > 0:
        # Skip a bit more to ensure we're past front matter
        skip_position = last_front_matter + 200
        if skip_position < len(text) * MAX_FRONT_MATTER_SKIP:
            return skip_position
    
    # Last resort: find first substantial paragraph after initial content
    # Look for first occurrence of multiple sentences (likely real content)
    sentences = re.finditer(r'[.!?]\s+[A-Z]', text[int(len(text) * MIN_FRONT_MATTER_SKIP):])
    first_sentences = list(sentences)[:5]  # First 5 sentence boundaries
    
    if len(first_sentences) >= 3:
        # We found substantial content
        return int(len(text) * MIN_FRONT_MATTER_SKIP) + first_sentences[0].start()
    
    return None


def _find_section_end(text: str, start_pos: int, max_search: int = 2000) -> int:
    """
    Find the end of a section starting at start_pos.
    
    Args:
        text: Full text
        start_pos: Starting position
        max_search: Maximum characters to search ahead
        
    Returns:
        End position of section
    """
    search_end = min(start_pos + max_search, len(text))
    search_text = text[start_pos:search_end]
    
    # Look for double line breaks (section breaks)
    double_break = re.search(r'\n\s*\n\s*\n', search_text)
    if double_break:
        return start_pos + double_break.end()
    
    # Look for single line break followed by capital letter (new section)
    section_break = re.search(r'\n\s*[A-Z][a-z]+\s*$', search_text, re.MULTILINE)
    if section_break:
        return start_pos + section_break.end()
    
    # Default: return position after reasonable section length
    return start_pos + min(500, len(search_text))

