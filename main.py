"""
Lamp of Knowledge - Main Entry Point

A screenless, voice-first device prototype that answers questions about books
from RFID codes. Optional narration available via 'read' command.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.rfid_manager import resolve_rfid
from core.pdf_loader import load_pdf
from core.chapter_detector import find_chapter_one_start
from core.session import Session
from core.narrator import Narrator
from core.command_router import CommandRouter
from llm.llm_router import LLMRouter
from config.settings import CHUNK_SIZE, NARRATION_DELAY
from config.prompts import SUCCESS_MESSAGES, ERROR_MESSAGES
from utils.logger import get_logger

logger = get_logger()


def main():
    """Main entry point for Lamp of Knowledge."""
    print("=" * 60)
    print("Lamp of Knowledge - Q&A Book Assistant")
    print("=" * 60)
    print()
    
    # Initialize LLM router
    try:
        llm_router = LLMRouter()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please configure your API keys in the .env file.")
        return 1
    except Exception as e:
        logger.error(f"Failed to initialize LLM router: {e}")
        print(f"Error initializing LLM service: {e}")
        return 1
    
    # Prompt for RFID code
    print("Scan RFID code: ", end="", flush=True)
    rfid_code = input().strip()
    
    if not rfid_code:
        print("Error: No RFID code provided.")
        return 1
    
    # Resolve RFID to book
    logger.info(f"Resolving RFID code: {rfid_code}")
    book_info = resolve_rfid(rfid_code)
    
    if not book_info:
        print(ERROR_MESSAGES["invalid_rfid"].format(rfid=rfid_code))
        return 1
    
    # Confirm book identity
    print(f"\n{SUCCESS_MESSAGES['book_loaded'].format(title=book_info['title'])}")
    print(f"Loading book from: {book_info['pdf_path']}\n")
    
    # Load PDF text
    logger.info(f"Loading PDF: {book_info['pdf_path']}")
    full_text = load_pdf(book_info['pdf_path'])
    
    if not full_text:
        print(ERROR_MESSAGES["pdf_load_failed"])
        return 1
    
    # Detect Chapter 1 start (for optional reading feature)
    logger.info("Detecting Chapter 1 start position")
    chapter_one_start = find_chapter_one_start(full_text)
    
    # Create session
    session = Session(
        book_title=book_info['title'],
        book_path=book_info['pdf_path'],
        full_text=full_text,
        chapter_one_start=chapter_one_start
    )
    
    # Initialize narrator (optional, only used if user requests reading)
    narrator = Narrator(session, full_text)
    
    # Initialize command router
    command_router = CommandRouter(narrator, llm_router)
    
    # Show welcome message and available commands
    print("\n" + "=" * 60)
    print("Book loaded successfully! Ask me anything about the book.")
    print("=" * 60)
    print("\nAvailable commands:")
    print("  ask: <question>  - Ask a question about the book")
    print("  read             - Start reading the book (optional)")
    print("  exit             - Exit the program")
    print("\nYou can also use these commands while reading:")
    print("  pause            - Pause reading")
    print("  continue         - Resume reading")
    print("  stop             - Stop reading")
    print("\n" + "-" * 60 + "\n")
    
    # Main command loop (Q&A focused)
    should_continue = True
    
    while should_continue:
        try:
            # Simple blocking input - wait for user command
            command = input("> ").strip()
            
            if not command:
                continue
            
            # Handle command
            should_continue = command_router.handle_command(command)
            
            # If narration is playing, print chunks continuously
            # User can interrupt with Ctrl+C, then use pause/stop commands
            if session.state == "playing":
                import time
                while session.state == "playing":
                    if session.current_position >= len(full_text):
                        print("\n[End of book reached]")
                        session.stop()
                        break
                    
                    # Print next chunk
                    has_more = narrator.narrate_chunk()
                    
                    if not has_more:
                        session.stop()
                        break
                    
                    # Small delay for readability
                    time.sleep(NARRATION_DELAY)
                    
        except KeyboardInterrupt:
            print("\n\nInterrupted. Exiting...")
            session.stop()
            should_continue = False
            break
        except EOFError:
            print("\n\nExiting...")
            session.stop()
            should_continue = False
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            print(f"Error: {e}")
            continue
    
    logger.info("Lamp of Knowledge session ended")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        logger.exception("Fatal error in main")
        print(f"\nFatal error: {e}")
        sys.exit(1)

