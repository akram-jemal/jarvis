# Lamp of Knowledge

A screenless, voice-first device prototype that automatically narrates books from RFID codes, starting from Chapter 1.

## Overview

Lamp of Knowledge is a command-line prototype for a future physical device that will:
- Read RFID codes from physical books
- Automatically extract and narrate content from local PDF files
- Start narration from Chapter 1 (skipping front matter)
- Answer questions about the book content using LLM APIs
- Support runtime commands (pause, continue, ask questions, etc.)

## Features

- **Automatic RFID Resolution**: Maps RFID codes to PDF files via JSON configuration
- **Smart Chapter Detection**: Automatically finds Chapter 1, skipping title pages, copyright, dedication, preface, and other front matter
- **Automatic Narration**: Begins reading immediately after RFID code is recognized
- **Question Answering**: Ask questions about the book content using OpenAI or Groq APIs
- **Runtime Commands**: Pause, continue, jump to chapters, ask questions, stop, or exit
- **Modular Architecture**: Hardware-ready for Raspberry Pi integration

## Project Structure

```
lamp_of_knowledge/
├── main.py                 # Entry point, RFID-driven flow
├── config/
│   ├── settings.py         # Global configuration
│   └── prompts.py          # LLM prompts and templates
├── core/
│   ├── rfid_manager.py     # Load & resolve RFID codes
│   ├── pdf_loader.py       # Extract text from PDF
│   ├── chapter_detector.py # Locate chapter boundaries
│   ├── narrator.py         # Auto-start narration engine
│   ├── command_router.py   # Runtime command handling
│   └── session.py          # Book + narration state
├── llm/
│   ├── openai_client.py    # ChatGPT API client
│   ├── groq_client.py      # Groq API client
│   └── llm_router.py       # Provider abstraction
├── data/
│   ├── books/              # PDF files directory
│   └── rfid_books.json     # RFID → PDF mapping
├── utils/
│   ├── text_chunker.py     # Chunk narration text
│   ├── logger.py           # Logging utility
│   └── helpers.py          # Helper functions
├── .env                    # Environment variables (API keys)
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

1. Copy the `.env` file and edit it:
   ```bash
   # On Windows, you may need to create the file manually
   ```

2. Add your API keys:
   - For OpenAI: Get your API key from https://platform.openai.com/api-keys
   - For Groq: Get your API key from https://console.groq.com/keys

3. Set your preferred LLM provider:
   ```
   LLM_PROVIDER=openai  # or "groq"
   ```

### 4. Configure RFID Mapping

Edit `data/rfid_books.json` to map RFID codes to your PDF files:

```json
{
  "RFID_001": {
    "title": "Your Book Title",
    "pdf_path": "data/books/your_book.pdf"
  }
}
```

### 5. Add PDF Files

Place your PDF files in the `data/books/` directory and update the paths in `rfid_books.json`.

**Note**: The system expects PDF files with a typical book structure:
- Title page
- Copyright page
- Table of Contents
- Chapters starting with "Chapter 1" or similar markers

## Running the Program

1. Start the program:
   ```bash
   python main.py
   ```

2. When prompted, enter an RFID code (e.g., `RFID_001`)

3. The system will:
   - Load the book
   - Detect Chapter 1
   - Automatically start narration
   - Display text chunks as "narration"

4. Use commands during narration:
   - `pause` - Pause narration
   - `continue` - Resume narration
   - `read chapter 1` - Jump to a specific chapter
   - `ask: <your question>` - Ask a question about the book
   - `stop` - Stop narration
   - `exit` - Exit the program

## Example Usage

```
Scan RFID code: RFID_001

Book loaded: Sample Book
Loading book from: data/books/sample_book.pdf

Starting Chapter One

[Book content chunk 1...]
[Book content chunk 2...]
[Book content chunk 3...]

ask: What is the main theme of this book?
[Answering your question: What is the main theme of this book?]

Answer: Based on the provided book content, the main theme appears to be...

Resuming narration...
[Book content chunk 4...]

pause
Narration paused.

continue
Resuming narration...
[Book content chunk 5...]

exit
Exiting Lamp of Knowledge. Goodbye!
```

## Configuration

Edit `config/settings.py` or set environment variables in `.env` to customize:

- `CHUNK_SIZE`: Characters per narration chunk (default: 500)
- `NARRATION_DELAY`: Seconds between chunks (default: 0.5)
- `LLM_PROVIDER`: "openai" or "groq" (default: "openai")
- `CONTEXT_CHUNKS_BEFORE/AFTER`: Context size for question answering
- `LOG_LEVEL`: Logging verbosity (INFO, WARNING, ERROR)

## Chapter Detection

The system automatically detects Chapter 1 using multiple patterns:

- "Chapter 1", "Chapter One", "CHAPTER 1"
- Numbered sections: "1.", "1. Introduction"
- Roman numerals: "I.", "Chapter I"

If no chapter marker is found, the system:
1. Looks for Table of Contents and starts after it
2. Skips common front matter (Copyright, Dedication, Preface, Foreword)
3. Falls back to skipping the first 5% of the document

## Question Answering

When you ask a question:
- The system extracts context around the current reading position
- Sends the question and context to the configured LLM
- The LLM is instructed to answer ONLY using the provided book content
- If the answer cannot be found in the book, it will say so
- Narration resumes automatically after answering (unless stopped)

## Architecture Notes

### Hardware-Ready Design

The code is structured to easily integrate with hardware:

- **RFID Scanner**: Replace `input()` in `main.py` with hardware reading
- **Audio Output**: Replace `print()` in `narrator.py` with TTS (text-to-speech)
- **Voice Commands**: Replace typed commands with STT (speech-to-text)

### Modular Components

- **RFID Manager**: Handles RFID-to-PDF mapping
- **PDF Loader**: Extracts text using pdfplumber
- **Chapter Detector**: Finds chapter boundaries
- **Narrator**: Manages narration state and chunk printing
- **Command Router**: Parses and handles user commands
- **LLM Router**: Abstracts different LLM providers

## Troubleshooting

### "RFID code not found"
- Check `data/rfid_books.json` for the correct RFID code
- Ensure the JSON file is valid

### "PDF file not found"
- Verify the PDF path in `rfid_books.json` is correct
- Check that the PDF file exists in the specified location
- Paths can be relative (to project root) or absolute

### "API key not configured"
- Ensure `.env` file exists in the project root
- Check that API keys are set correctly
- Verify `LLM_PROVIDER` matches the API key you configured

### Chapter detection issues
- Ensure PDF has clear chapter markers ("Chapter 1", etc.)
- Check that PDF text extraction is working (see logs)
- Manually verify the PDF structure matches expected format

### Narration not starting
- Check logs for errors in PDF loading or chapter detection
- Verify the PDF contains readable text (not scanned images)
- Ensure Chapter 1 is detectable (see Chapter Detection section)

## Logs

Logs are written to:
- Console: Real-time output
- File: `data/lamp_of_knowledge.log` (detailed logs)

Set `LOG_LEVEL` in `.env` to control verbosity.

## Future Enhancements

Potential improvements for hardware integration:

1. **Audio Output**: Integrate TTS engine (e.g., pyttsx3, gTTS)
2. **Voice Input**: Add STT for voice commands (e.g., SpeechRecognition)
3. **RFID Hardware**: Interface with RFID reader (e.g., via serial port)
4. **Session Persistence**: Save reading position to resume later
5. **Chapter Navigation**: Build full chapter map for better navigation
6. **Bookmarks**: Save and restore reading positions
7. **Multi-language**: Support for non-English books

## License

This is a prototype implementation for demonstration purposes.

## Author

Senior Software Architect - Lamp of Knowledge Project

