"""
Memory Retrieval Module
Retrieves relevant memories based on user queries for context enhancement.
"""

from typing import List, Dict
from memory.vector_store import VectorMemoryStore

class MemoryRetriever:
    """
    Handles intelligent retrieval of relevant conversation memories
    to provide context for LLM responses.
    """
    
    def __init__(self, vector_store: VectorMemoryStore, top_k: int = 3):
        """
        Initialize the memory retriever.
        
        Args:
            vector_store: VectorMemoryStore instance
            top_k: Default number of memories to retrieve
        """
        self.vector_store = vector_store
        self.top_k = top_k
    
    def retrieve_relevant_memories(self, query: str, top_k: int = None) -> List[str]:
        """
        Retrieve most relevant memories for a given query.
        
        Args:
            query: User's current message/question
            top_k: Number of memories to retrieve (uses default if None)
            
        Returns:
            List of relevant memory summary strings
            
        Example:
            >>> retriever = MemoryRetriever(vector_store)
            >>> memories = retriever.retrieve_relevant_memories("Tell me about databases")
            >>> print(memories[0])
            "User is studying DBMS for GATE exam..."
        """
        if top_k is None:
            top_k = self.top_k
        
        # Search vector store for similar memories
        results = self.vector_store.search_memories(query, top_k=top_k)
        
        # Extract and return just the summary texts
        memories = [result['summary'] for result in results]
        
        return memories
    
    def retrieve_with_metadata(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Retrieve memories with full metadata.
        
        Args:
            query: User's current message/question
            top_k: Number of memories to retrieve
            
        Returns:
            List of memory dicts with id, summary, distance, and metadata
        """
        if top_k is None:
            top_k = self.top_k
        
        return self.vector_store.search_memories(query, top_k=top_k)
    
    def retrieve_recent_memories(self, count: int = 5) -> List[str]:
        """
        Retrieve the most recent memories regardless of relevance.
        
        Args:
            count: Number of recent memories to retrieve
            
        Returns:
            List of recent memory summaries
        """
        all_memories = self.vector_store.get_all_memories()
        
        # Sort by timestamp (newest first)
        sorted_memories = sorted(
            all_memories,
            key=lambda x: x.get('metadata', {}).get('timestamp', ''),
            reverse=True
        )
        
        # Get the most recent ones
        recent = sorted_memories[:count]
        return [mem['summary'] for mem in recent]
    
    def format_memories_for_prompt(self, memories: List[str]) -> str:
        """
        Format retrieved memories into a readable string for LLM prompt.
        
        Args:
            memories: List of memory summary strings
            
        Returns:
            Formatted string suitable for including in LLM prompt
            
        Example:
            >>> memories = ["Memory 1...", "Memory 2..."]
            >>> formatted = retriever.format_memories_for_prompt(memories)
            >>> print(formatted)
            '''
            Relevant past memories:
            1. Memory 1...
            2. Memory 2...
            '''
        """
        if not memories:
            return "No relevant past memories found."
        
        formatted_lines = ["Relevant past memories:"]
        for i, memory in enumerate(memories, 1):
            formatted_lines.append(f"{i}. {memory}")
        
        return "\n".join(formatted_lines)
    
    def has_relevant_memories(self, query: str, similarity_threshold: float = 0.5) -> bool:
        """
        Check if there are any relevant memories above a similarity threshold.
        
        Args:
            query: User's query
            similarity_threshold: Minimum similarity score (lower distance = higher similarity)
            
        Returns:
            True if relevant memories exist, False otherwise
        """
        results = self.vector_store.search_memories(query, top_k=1)
        
        if not results:
            return False
        
        # Check if the closest match is relevant enough
        # Note: distance is inverse of similarity (lower is better)
        if results[0].get('distance') is not None:
            return results[0]['distance'] < similarity_threshold
        
        return True  # If no distance metric, assume relevant
    
    def get_memory_statistics(self) -> Dict:
        """
        Get statistics about stored memories.
        
        Returns:
            Dict with statistics like total count, topics, etc.
        """
        all_memories = self.vector_store.get_all_memories()
        
        # Collect all topics from metadata
        all_topics = []
        for mem in all_memories:
            topics = mem.get('metadata', {}).get('topics', [])
            all_topics.extend(topics)
        
        # Count topic frequencies
        topic_counts = {}
        for topic in all_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        return {
            'total_memories': len(all_memories),
            'topic_distribution': topic_counts,
            'has_memories': len(all_memories) > 0
        }


# Example usage
if __name__ == "__main__":
    from memory.vector_store import VectorMemoryStore
    
    # Initialize components
    vector_store = VectorMemoryStore()
    retriever = MemoryRetriever(vector_store, top_k=3)
    
    # Store some test memories
    vector_store.store_memory(
        "User is preparing for GATE CS exam. Weak in OS and DBMS.",
        metadata={"topics": ["GATE", "OS", "DBMS"]}
    )
    vector_store.store_memory(
        "User discussed Indian constitutional law and J Sai Deepak's work.",
        metadata={"topics": ["law", "constitution"]}
    )
    
    # Test retrieval
    print("Test Query: 'Help me understand database concepts'")
    memories = retriever.retrieve_relevant_memories("Help me understand database concepts")
    
    print("\nRetrieved Memories:")
    formatted = retriever.format_memories_for_prompt(memories)
    print(formatted)
    
    # Get statistics
    print("\nMemory Statistics:")
    stats = retriever.get_memory_statistics()
    print(f"Total memories: {stats['total_memories']}")
    print(f"Topics: {stats['topic_distribution']}")
