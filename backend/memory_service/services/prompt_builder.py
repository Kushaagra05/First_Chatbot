"""
Prompt Builder Service
Constructs LLM prompts with memory context and recent conversation history.
"""

from typing import List, Dict

class PromptBuilder:
    """
    Builds structured prompts for LLM that include:
    - System context
    - Relevant memories
    - Recent conversation
    - Current user query
    """
    
    def __init__(self, personality_prompt: str = None):
        """
        Initialize prompt builder with optional personality setting.
        
        Args:
            personality_prompt: Custom system personality (e.g., J Sai Deepak style)
        """
        self.personality_prompt = personality_prompt or self._default_personality()
    
    def _default_personality(self) -> str:
        """
        Default system personality prompt.
        
        Returns:
            Default personality string
        """
        return """You are a helpful AI assistant. Provide clear, accurate, and informative responses to user questions. Be conversational, friendly, and helpful.

Use the provided past memories to maintain context and continuity across conversations."""
    
    def build_prompt(
        self,
        query: str,
        memories: List[str] = None,
        recent_history: List[Dict[str, str]] = None
    ) -> List[Dict[str, str]]:
        """
        Build a complete prompt with all context for the LLM.
        
        Args:
            query: Current user message/question
            memories: List of relevant memory summaries
            recent_history: Recent conversation messages (last few exchanges)
            
        Returns:
            List of message dicts formatted for OpenAI API
            
        Example:
            >>> builder = PromptBuilder()
            >>> messages = builder.build_prompt(
            ...     query="What is your view on this?",
            ...     memories=["User studies law..."],
            ...     recent_history=[{"role": "user", "content": "Hi"}]
            ... )
        """
        messages = []
        
        # 1. System prompt with personality
        system_content = self.personality_prompt
        
        # 2. Add memory context if available
        if memories and len(memories) > 0:
            memory_context = self._format_memory_context(memories)
            system_content += f"\n\n{memory_context}"
        
        messages.append({
            "role": "system",
            "content": system_content
        })
        
        # 3. Add recent conversation history
        if recent_history:
            messages.extend(recent_history)
        
        # 4. Add current user query
        messages.append({
            "role": "user",
            "content": query
        })
        
        return messages
    
    def _format_memory_context(self, memories: List[str]) -> str:
        """
        Format memories into a structured context string.
        
        Args:
            memories: List of memory summaries
            
        Returns:
            Formatted memory context string
        """
        if not memories:
            return ""
        
        context_lines = ["=== RELEVANT PAST CONTEXT ==="]
        context_lines.append("Use this information to maintain continuity:\n")
        
        for i, memory in enumerate(memories, 1):
            context_lines.append(f"Memory {i}: {memory}")
        
        context_lines.append("\n=== END CONTEXT ===")
        return "\n".join(context_lines)
    
    def build_simple_prompt(self, query: str) -> List[Dict[str, str]]:
        """
        Build a simple prompt without memories (for short conversations).
        
        Args:
            query: User's message
            
        Returns:
            Simple message list for LLM
        """
        return [
            {"role": "system", "content": self.personality_prompt},
            {"role": "user", "content": query}
        ]
    
    def set_personality(self, personality_prompt: str):
        """
        Update the system personality prompt.
        
        Args:
            personality_prompt: New personality description
        """
        self.personality_prompt = personality_prompt
    
    def format_conversation_for_display(
        self,
        memories: List[str],
        recent_history: List[Dict[str, str]],
        current_query: str
    ) -> str:
        """
        Format the full context in a readable way (for debugging/logging).
        
        Args:
            memories: Relevant memories
            recent_history: Recent messages
            current_query: Current user query
            
        Returns:
            Formatted string showing the full context
        """
        lines = []
        
        # System personality
        lines.append("=== SYSTEM PERSONALITY ===")
        lines.append(self.personality_prompt[:200] + "...")
        lines.append("")
        
        # Memories
        if memories:
            lines.append("=== MEMORIES ===")
            for i, mem in enumerate(memories, 1):
                lines.append(f"{i}. {mem}")
            lines.append("")
        
        # Recent conversation
        if recent_history:
            lines.append("=== RECENT CONVERSATION ===")
            for msg in recent_history:
                role = msg['role'].capitalize()
                content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                lines.append(f"{role}: {content}")
            lines.append("")
        
        # Current query
        lines.append("=== CURRENT QUERY ===")
        lines.append(current_query)
        
        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    # Initialize prompt builder
    builder = PromptBuilder()
    
    # Sample data
    memories = [
        "User is preparing for GATE CS exam. Weak in OS and DBMS.",
        "User expressed interest in Indian constitutional law."
    ]
    
    recent_history = [
        {"role": "user", "content": "What are the key concepts in DBMS?"},
        {"role": "assistant", "content": "Key DBMS concepts include normalization, transactions..."}
    ]
    
    current_query = "Can you explain database normalization?"
    
    # Build prompt
    messages = builder.build_prompt(
        query=current_query,
        memories=memories,
        recent_history=recent_history[-2:]  # Last 2 messages
    )
    
    print("=== BUILT PROMPT ===")
    for msg in messages:
        print(f"\n{msg['role'].upper()}:")
        print(msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content'])
