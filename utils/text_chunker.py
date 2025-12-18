"""
Text chunking utilities for narration.
"""
import re
from typing import List, Tuple


def chunk_text(text: str, chunk_size: int = 500) -> List[Tuple[str, int]]:
    """
    Split text into readable chunks preserving sentence boundaries.
    
    Args:
        text: Text to chunk
        chunk_size: Target chunk size in characters
        
    Returns:
        List of tuples: (chunk_text, start_position)
    """
    if not text:
        return []
    
    chunks = []
    current_pos = 0
    
    # Split by paragraphs first
    paragraphs = text.split('\n\n')
    
    current_chunk = ""
    chunk_start = current_pos
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        # If adding this paragraph would exceed chunk size
        if current_chunk and len(current_chunk) + len(para) + 2 > chunk_size:
            # Save current chunk
            chunks.append((current_chunk.strip(), chunk_start))
            
            # Start new chunk
            current_chunk = para
            chunk_start = current_pos
        else:
            # Add paragraph to current chunk
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para
                chunk_start = current_pos
        
        current_pos += len(para) + 2  # +2 for \n\n
        
        # If current chunk exceeds chunk_size, split by sentences
        while len(current_chunk) > chunk_size:
            # Find last sentence boundary before chunk_size
            sentences = re.split(r'([.!?]\s+)', current_chunk[:chunk_size * 2])
            
            if len(sentences) > 2:
                # Take complete sentences
                sentence_text = ""
                new_start = chunk_start
                for i in range(0, len(sentences) - 1, 2):
                    if i + 1 < len(sentences):
                        sent = sentences[i] + sentences[i + 1]
                        if len(sentence_text) + len(sent) <= chunk_size:
                            sentence_text += sent
                            new_start += len(sent)
                        else:
                            break
                
                if sentence_text:
                    chunks.append((sentence_text.strip(), chunk_start))
                    current_chunk = current_chunk[len(sentence_text):]
                    chunk_start = new_start
                else:
                    # Fallback: split at word boundary
                    words = current_chunk[:chunk_size].rsplit(' ', 1)
                    if len(words) == 2:
                        chunks.append((words[0].strip(), chunk_start))
                        current_chunk = words[1] + current_chunk[chunk_size:]
                        chunk_start += len(words[0]) + 1
                    else:
                        chunks.append((current_chunk[:chunk_size].strip(), chunk_start))
                        current_chunk = current_chunk[chunk_size:]
                        chunk_start += chunk_size
            else:
                # No sentence boundaries found, split at word
                words = current_chunk[:chunk_size].rsplit(' ', 1)
                if len(words) == 2:
                    chunks.append((words[0].strip(), chunk_start))
                    current_chunk = words[1] + current_chunk[chunk_size:]
                    chunk_start += len(words[0]) + 1
                else:
                    chunks.append((current_chunk[:chunk_size].strip(), chunk_start))
                    current_chunk = current_chunk[chunk_size:]
                    chunk_start += chunk_size
    
    # Add remaining chunk
    if current_chunk.strip():
        chunks.append((current_chunk.strip(), chunk_start))
    
    return chunks


def get_text_chunk_at_position(text: str, position: int, chunk_size: int = 500) -> str:
    """
    Extract a chunk of text starting at a specific position.
    
    Args:
        text: Full text
        position: Start position
        chunk_size: Target chunk size
        
    Returns:
        Chunk text
    """
    if position >= len(text):
        return ""
    
    # Get text from position
    remaining_text = text[position:]
    
    # Chunk it and return first chunk
    chunks = chunk_text(remaining_text, chunk_size)
    if chunks:
        return chunks[0][0]
    return ""

