"""
Narration engine that automatically starts reading from Chapter 1.
"""
import time
from typing import Optional
from core.session import Session
from utils.text_chunker import chunk_text, get_text_chunk_at_position
from utils.helpers import extract_context_around_position
from config.settings import CHUNK_SIZE, NARRATION_DELAY, CONTEXT_CHUNKS_BEFORE, CONTEXT_CHUNKS_AFTER
from config.prompts import SUCCESS_MESSAGES
from utils.logger import get_logger

logger = get_logger()


class Narrator:
    """Manages automatic narration of book content."""
    
    def __init__(self, session: Session, full_text: str):
        """
        Initialize narrator with session and full text.
        
        Args:
            session: Session object tracking narration state
            full_text: Complete book text
        """
        self.session = session
        self.full_text = full_text
        self.session.full_text = full_text
        logger.info(f"Narrator initialized for book: {session.book_title}")
    
    def start(self):
        """
        Automatically start narration from Chapter 1.
        This is called immediately after RFID resolution.
        Sets up the session but does not block - main loop handles narration.
        """
        if not self.full_text:
            logger.error("Cannot start narration: no text available")
            return
        
        # Set position to Chapter 1 start
        self.session.current_position = self.session.chapter_one_start
        self.session.state = "playing"
        self.session.current_chapter = 1
        
        # Print starting message
        print(f"\n{SUCCESS_MESSAGES['narration_started']}\n")
        logger.info("Narration started from Chapter 1")
    
    def narrate_chunk(self) -> bool:
        """
        Narrate a single chunk (used when resuming after pause).
        
        Returns:
            True if more text available, False if end reached
        """
        if self.session.current_position >= len(self.full_text):
            return False
        
        chunk_text = get_text_chunk_at_position(
            self.full_text,
            self.session.current_position,
            CHUNK_SIZE
        )
        
        if not chunk_text:
            return False
        
        print(chunk_text)
        print()
        
        chunk_length = len(chunk_text)
        self.session.add_chunk(chunk_text, self.session.current_position)
        self.session.update_position(self.session.current_position + chunk_length)
        
        return True
    
    def pause(self):
        """Pause narration."""
        self.session.pause()
        logger.info("Narration paused")
    
    def continue_narration(self):
        """Resume narration from last position."""
        if self.session.state == "paused":
            self.session.resume()
            print(f"\n{SUCCESS_MESSAGES['narration_resumed']}\n")
            logger.info("Narration resumed")
    
    def jump_to_chapter(self, chapter_num: int):
        """
        Jump to a specific chapter number.
        
        Args:
            chapter_num: Chapter number to jump to
        """
        # For now, we only support Chapter 1 auto-detection
        # Full chapter navigation would require building a chapter map
        if chapter_num == 1:
            self.session.current_position = self.session.chapter_one_start
            self.session.current_chapter = 1
            print(f"{SUCCESS_MESSAGES['chapter_jumped'].format(number=chapter_num)}\n")
        else:
            print(f"Note: Jumping to Chapter {chapter_num} is not yet implemented. Remaining at current position.")
            logger.warning(f"Jump to Chapter {chapter_num} requested but not implemented")
    
    def stop(self):
        """Stop narration completely."""
        self.session.stop()
        logger.info("Narration stopped")
    
    def get_context_for_question(self) -> str:
        """
        Get text context around current position for question answering.
        
        Returns:
            Context text
        """
        context_size = (CONTEXT_CHUNKS_BEFORE + CONTEXT_CHUNKS_AFTER + 1) * CHUNK_SIZE
        return extract_context_around_position(
            self.full_text,
            self.session.current_position,
            context_size
        )

