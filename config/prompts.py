"""
LLM prompts and message templates for Lamp of Knowledge.
"""
from config.settings import CONTEXT_CHUNKS_BEFORE, CONTEXT_CHUNKS_AFTER

# System prompt for question answering - strictly prevents hallucination
QUESTION_ANSWER_SYSTEM_PROMPT = """You are a helpful assistant that answers questions based ONLY on the provided book content.

CRITICAL RULES:
1. Answer questions using ONLY the text provided from the book
2. If the answer cannot be found in the provided book content, you MUST respond with: "I cannot answer that question based on the book content."
3. Do NOT make up information
4. Do NOT use knowledge from outside the provided book content
5. Be concise and accurate
6. Quote relevant passages when helpful, but keep quotes brief

Book content will be provided in the user's message."""

# User prompt template for question answering
QUESTION_ANSWER_USER_PROMPT_TEMPLATE = """Based on the following book content, answer this question: "{question}"

Book Content:
{book_context}

Remember: Answer ONLY using the provided book content. If the answer is not in the content, say so."""

def get_question_prompt(question: str, book_context: str) -> dict:
    """
    Generate prompt dict for question answering.
    
    Args:
        question: User's question
        book_context: Relevant book text to use for answering
        
    Returns:
        Dict with system and user messages
    """
    return {
        "system": QUESTION_ANSWER_SYSTEM_PROMPT,
        "user": QUESTION_ANSWER_USER_PROMPT_TEMPLATE.format(
            question=question,
            book_context=book_context
        )
    }

# Error messages
ERROR_MESSAGES = {
    "invalid_rfid": "Error: RFID code '{rfid}' not found in library.",
    "pdf_not_found": "Error: PDF file not found at '{path}'.",
    "pdf_load_failed": "Error: Failed to load PDF. Please check the file format.",
    "no_chapter_found": "Warning: Could not detect Chapter 1. Starting from estimated position.",
    "invalid_command": "Error: Invalid command. Available commands: ask: <question>, read, pause, continue, stop, exit",
    "api_error": "Error: Failed to communicate with LLM service. Please check your API keys and connection.",
    "no_context": "Error: Cannot answer question. No book context available."
}

# Success messages
SUCCESS_MESSAGES = {
    "book_loaded": "Book loaded: {title}",
    "chapter_detected": "Chapter {number} detected. Starting narration...",
    "narration_started": "Starting Chapter One",
    "narration_paused": "Narration paused.",
    "narration_resumed": "Resuming narration...",
    "narration_stopped": "Narration stopped.",
    "chapter_jumped": "Jumped to Chapter {number}."
}

