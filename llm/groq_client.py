"""
Groq API client for question answering.
"""
import time
from typing import Optional
from groq import Groq
from config.settings import GROQ_API_KEY, API_TIMEOUT, API_MAX_RETRIES, API_RETRY_DELAY
from config.prompts import get_question_prompt
from utils.logger import get_logger

logger = get_logger()


class GroqClient:
    """Client for Groq API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Groq client.
        
        Args:
            api_key: Groq API key (defaults to config setting)
        """
        self.api_key = api_key or GROQ_API_KEY
        if not self.api_key:
            raise ValueError("Groq API key not provided")
        
        self.client = Groq(api_key=self.api_key)
        logger.info("Groq client initialized")
    
    def answer_question(self, question: str, book_context: str) -> str:
        """
        Answer a question using book context via Groq API.
        
        Args:
            question: User's question
            book_context: Relevant book text context
            
        Returns:
            Answer string
        """
        prompt = get_question_prompt(question, book_context)
        
        for attempt in range(API_MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    model="groq/compound-mini",
                    messages=[
                        {"role": "system", "content": prompt["system"]},
                        {"role": "user", "content": prompt["user"]}
                    ],
                    temperature=0.3,  # Lower temperature for more focused answers
                    max_tokens=500,
                    timeout=API_TIMEOUT
                )
                
                answer = response.choices[0].message.content.strip()
                logger.info(f"Groq answered question successfully")
                return answer
                
            except Exception as e:
                logger.warning(f"Groq API attempt {attempt + 1} failed: {e}")
                if attempt < API_MAX_RETRIES - 1:
                    time.sleep(API_RETRY_DELAY * (attempt + 1))
                else:
                    logger.error(f"Groq API failed after {API_MAX_RETRIES} attempts")
                    return "I apologize, but I encountered an error while trying to answer your question. Please try again."

