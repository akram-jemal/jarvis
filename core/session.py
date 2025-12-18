"""
Session state management for book narration.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from pathlib import Path


@dataclass
class Session:
    """Manages current book and narration state."""
    
    book_title: str = ""
    book_path: Path = Path()
    full_text: str = ""
    chapter_one_start: int = 0
    current_position: int = 0
    current_chapter: int = 1
    state: str = "stopped"  # "playing", "paused", "stopped"
    narrated_chunks: List[Dict[str, Any]] = field(default_factory=list)
    
    def update_position(self, new_position: int):
        """Update current reading position."""
        self.current_position = new_position
    
    def add_chunk(self, chunk_text: str, position: int):
        """Record a narrated chunk."""
        self.narrated_chunks.append({
            "text": chunk_text,
            "position": position,
            "chapter": self.current_chapter
        })
    
    def pause(self):
        """Pause narration."""
        if self.state == "playing":
            self.state = "paused"
    
    def resume(self):
        """Resume narration."""
        if self.state == "paused":
            self.state = "playing"
    
    def stop(self):
        """Stop narration."""
        self.state = "stopped"
    
    def start(self):
        """Start narration."""
        self.state = "playing"
        self.current_position = self.chapter_one_start
    
    def jump_to_chapter(self, chapter_num: int):
        """Jump to a specific chapter (placeholder - requires chapter positions)."""
        self.current_chapter = chapter_num
        # Position update would need chapter positions map
        # For now, just update chapter number
    
    def get_context_for_question(self, chunks_before: int = 2, chunks_after: int = 2) -> str:
        """
        Get text context around current position for question answering.
        
        Args:
            chunks_before: Number of chunks before current position
            chunks_after: Number of chunks after current position
            
        Returns:
            Context text
        """
        # Get text around current position
        context_size = (chunks_before + chunks_after + 1) * 500  # Rough estimate
        start_pos = max(0, self.current_position - (chunks_before * 500))
        end_pos = min(len(self.full_text), self.current_position + (chunks_after * 500))
        
        return self.full_text[start_pos:end_pos]
    
    def get_full_book_context(self) -> str:
        """
        Get the entire book text for question answering.
        
        Returns:
            Full book text
        """
        return self.full_text

