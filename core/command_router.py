"""
Command router for handling runtime commands during narration.
"""
import re
from typing import Optional
from core.narrator import Narrator
from llm.llm_router import LLMRouter
from config.prompts import ERROR_MESSAGES
from utils.logger import get_logger

logger = get_logger()


class CommandRouter:
    """Routes and handles user commands during narration."""
    
    def __init__(self, narrator: Narrator, llm_router: LLMRouter):
        """
        Initialize command router.
        
        Args:
            narrator: Narrator instance
            llm_router: LLM router instance for question answering
        """
        self.narrator = narrator
        self.llm_router = llm_router
        logger.info("Command router initialized")
    
    def handle_command(self, command: str) -> bool:
        """
        Parse and handle a user command.
        
        Args:
            command: User input command
            
        Returns:
            True if should continue, False if should exit
        """
        command_lower = command.strip().lower()
        
        if not command:
            return True
        
        # Ask command (PRIMARY FEATURE - Q&A)
        ask_match = re.match(r'ask:\s*(.+)', command, re.IGNORECASE)
        if ask_match:
            question = ask_match.group(1).strip()
            self._handle_question(question)
            return True
        
        # Read command (optional narration)
        if command_lower == "read":
            self.narrator.start()
            return True
        
        # Pause command (for narration)
        if command_lower == "pause":
            if self.narrator.session.state == "playing":
                self.narrator.pause()
            else:
                print("No narration is currently playing.")
            return True
        
        # Continue command (for narration)
        if command_lower == "continue":
            if self.narrator.session.state == "paused":
                self.narrator.continue_narration()
            else:
                print("No narration is paused.")
            return True
        
        # Read chapter command (optional)
        chapter_match = re.match(r'read\s+chapter\s+(\d+)', command_lower)
        if chapter_match:
            chapter_num = int(chapter_match.group(1))
            self.narrator.jump_to_chapter(chapter_num)
            self.narrator.start()
            return True
        
        # Stop command (for narration)
        if command_lower == "stop":
            if self.narrator.session.state in ["playing", "paused"]:
                self.narrator.stop()
                print("Narration stopped.")
            else:
                print("No narration is currently active.")
            return True
        
        # Exit command
        if command_lower == "exit":
            if self.narrator.session.state in ["playing", "paused"]:
                self.narrator.stop()
            print("Exiting Lamp of Knowledge. Goodbye!")
            return False
        
        # Invalid command
        print(ERROR_MESSAGES["invalid_command"])
        return True
    
    def _handle_question(self, question: str):
        """
        Handle a question using entire book content as context.
        
        Args:
            question: User's question
        """
        # Pause narration if playing (so user can see the answer clearly)
        was_playing = self.narrator.session.state == "playing"
        if was_playing:
            self.narrator.pause()
        
        print(f"\n[Answering your question: {question}]\n")
        
        # Get full book context (entire book text)
        context = self.narrator.session.get_context_for_question(
            chunks_before=5,
            chunks_after=5,
        )
        
        if not context:
            print(ERROR_MESSAGES["no_context"])
            return
        
        try:
            # Get answer from LLM using entire book content
            answer = self.llm_router.answer_question(question, context)
            print(f"Answer: {answer}\n")
            
            # Resume narration if it was playing (unless user stopped it)
            if was_playing and self.narrator.session.state == "paused":
                print("Resuming narration...\n")
                self.narrator.continue_narration()
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            print(f"{ERROR_MESSAGES['api_error']}\n")
            # Still try to resume if it was playing
            if was_playing and self.narrator.session.state == "paused":
                self.narrator.continue_narration()

