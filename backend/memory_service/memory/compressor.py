"""
Memory Compression Module
Compresses conversation history into summarized memories using LLM.
"""

import os
from openai import OpenAI
from typing import List, Dict

class MemoryCompressor:
    """
    Compresses older conversation messages into concise summaries
    that capture key information, entities, and topics.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the memory compressor with OpenAI API.
        
        Args:
            api_key: OpenAI API key. If None, reads from environment.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)
        
    def compress_conversation(self, history: List[Dict[str, str]]) -> str:
        """
        Compress a segment of conversation history into a structured summary.
        
        Args:
            history: List of message dicts with 'role' and 'content' keys
            
        Returns:
            Compressed summary string containing key information
            
        Example:
            >>> history = [
            ...     {"role": "user", "content": "I'm studying for GATE"},
            ...     {"role": "assistant", "content": "Great! What subjects?"}
            ... ]
            >>> summary = compressor.compress_conversation(history)
            >>> print(summary)
            "User is preparing for GATE exam..."
        """
        # Build conversation text from history
        conversation_text = self._format_conversation(history)
        
        # Create compression prompt
        compression_prompt = f"""Analyze the following conversation and create a concise structured summary that captures:
1. Main topics discussed
2. Key facts and information shared by the user
3. User's goals, preferences, or problems mentioned
4. Important entities (names, places, concepts)

Be specific and factual. Keep the summary under 200 words.

Conversation:
{conversation_text}

Summary:"""

        try:
            # Call OpenAI API for summarization
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a precise conversation summarizer."},
                    {"role": "user", "content": compression_prompt}
                ],
                temperature=0.3,  # Lower temperature for more factual summaries
                max_tokens=300
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            print(f"Error compressing conversation: {e}")
            # Fallback: Return a basic summary
            return self._create_fallback_summary(history)
    
    def _format_conversation(self, history: List[Dict[str, str]]) -> str:
        """
        Format conversation history into readable text.
        
        Args:
            history: List of message dicts
            
        Returns:
            Formatted conversation string
        """
        formatted = []
        for msg in history:
            role = "User" if msg['role'] == 'user' else "Assistant"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted)
    
    def _create_fallback_summary(self, history: List[Dict[str, str]]) -> str:
        """
        Create a basic summary when API call fails.
        
        Args:
            history: List of message dicts
            
        Returns:
            Simple summary string
        """
        user_messages = [msg['content'] for msg in history if msg['role'] == 'user']
        topics = ', '.join(user_messages[:3])  # First 3 user messages
        return f"Conversation covered topics including: {topics}"


# Example usage
if __name__ == "__main__":
    # Test the compressor
    compressor = MemoryCompressor()
    
    test_history = [
        {"role": "user", "content": "I'm preparing for the GATE Computer Science exam"},
        {"role": "assistant", "content": "That's great! GATE CS covers several important subjects."},
        {"role": "user", "content": "I'm weak in Operating Systems and DBMS"},
        {"role": "assistant", "content": "Let me help you with those topics."},
        {"role": "user", "content": "I already know SQL basics though"},
        {"role": "assistant", "content": "Good! That will help with DBMS."}
    ]
    
    summary = compressor.compress_conversation(test_history)
    print("Compressed Summary:")
    print(summary)
