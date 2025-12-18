"""
LLM provider router for abstracting different LLM services.
"""
from typing import Optional
from config.settings import LLM_PROVIDER, OPENAI_API_KEY, GROQ_API_KEY
from llm.openai_client import OpenAIClient
from llm.groq_client import GroqClient
from utils.logger import get_logger

logger = get_logger()


class LLMRouter:
    """Routes question answering requests to configured LLM provider."""
    
    def __init__(self, provider: Optional[str] = None):
        """
        Initialize LLM router with specified provider.
        
        Args:
            provider: Provider name ("openai" or "groq"), defaults to config setting
            
        Raises:
            ValueError: If provider is invalid or API key is missing
        """
        self.provider_name = provider or LLM_PROVIDER.lower()
        
        if self.provider_name == "openai":
            if not OPENAI_API_KEY:
                raise ValueError("OpenAI API key not configured. Set OPENAI_API_KEY in .env")
            self.client = OpenAIClient()
        elif self.provider_name == "groq":
            if not GROQ_API_KEY:
                raise ValueError("Groq API key not configured. Set GROQ_API_KEY in .env")
            self.client = GroqClient()
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider_name}. Use 'openai' or 'groq'")
        
        logger.info(f"LLM Router initialized with provider: {self.provider_name}")
    
    def answer_question(self, question: str, book_context: str) -> str:
        """
        Answer a question using the configured LLM provider.
        
        Args:
            question: User's question
            book_context: Relevant book text context
            
        Returns:
            Answer string
        """
        return self.client.answer_question(question, book_context)

