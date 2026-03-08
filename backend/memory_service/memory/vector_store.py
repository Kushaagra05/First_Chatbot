"""
Vector Memory Storage Module
Stores conversation summaries with embeddings in ChromaDB vector database.
"""

import os
from datetime import datetime
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

class VectorMemoryStore:
    """
    Manages storage and retrieval of conversation memories in a vector database.
    Uses ChromaDB for persistent storage and SentenceTransformers for embeddings.
    """
    
    def __init__(self, persist_dir: str = "./chroma_db", collection_name: str = "conversation_memories"):
        """
        Initialize the vector store with ChromaDB and embedding model.
        
        Args:
            persist_dir: Directory to persist ChromaDB data
            collection_name: Name of the collection to store memories
        """
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Compressed conversation memories"}
        )
        
        # Initialize embedding model (lightweight and efficient)
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print("Embedding model loaded successfully")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for input text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def store_memory(self, summary: str, metadata: Optional[Dict] = None) -> str:
        """
        Store a compressed memory summary with its embedding.
        
        Args:
            summary: Compressed conversation summary text
            metadata: Optional metadata (topics, entities, etc.)
            
        Returns:
            memory_id: Unique ID of the stored memory
            
        Example:
            >>> store = VectorMemoryStore()
            >>> memory_id = store.store_memory(
            ...     "User is preparing for GATE exam...",
            ...     metadata={"topics": ["GATE", "OS", "DBMS"]}
            ... )
        """
        # Generate unique ID based on timestamp
        memory_id = f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Generate embedding for the summary
        embedding = self.generate_embedding(summary)
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "timestamp": datetime.now().isoformat(),
            "summary": summary
        })
        
        # Store in ChromaDB
        self.collection.add(
            ids=[memory_id],
            embeddings=[embedding],
            documents=[summary],
            metadatas=[metadata]
        )
        
        print(f"Memory stored with ID: {memory_id}")
        return memory_id
    
    def search_memories(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search for relevant memories using semantic similarity.
        
        Args:
            query: Query text to search for
            top_k: Number of top relevant memories to return
            
        Returns:
            List of memory dicts with 'id', 'summary', 'distance', and 'metadata'
            
        Example:
            >>> results = store.search_memories("Tell me about operating systems", top_k=3)
            >>> for result in results:
            ...     print(result['summary'])
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query)
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Format results
        memories = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                memory = {
                    'id': results['ids'][0][i],
                    'summary': results['documents'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None,
                    'metadata': results['metadatas'][0][i] if 'metadatas' in results else {}
                }
                memories.append(memory)
        
        print(f"Found {len(memories)} relevant memories")
        return memories
    
    def get_all_memories(self) -> List[Dict]:
        """
        Retrieve all stored memories.
        
        Returns:
            List of all memory dicts
        """
        results = self.collection.get()
        memories = []
        
        if results['ids']:
            for i in range(len(results['ids'])):
                memory = {
                    'id': results['ids'][i],
                    'summary': results['documents'][i],
                    'metadata': results['metadatas'][i] if 'metadatas' in results else {}
                }
                memories.append(memory)
        
        return memories
    
    def delete_memory(self, memory_id: str):
        """
        Delete a specific memory by ID.
        
        Args:
            memory_id: ID of memory to delete
        """
        self.collection.delete(ids=[memory_id])
        print(f"Memory {memory_id} deleted")
    
    def clear_all_memories(self):
        """
        Delete all memories from the collection.
        Warning: This action cannot be undone!
        """
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Compressed conversation memories"}
        )
        print("All memories cleared")
    
    def get_memory_count(self) -> int:
        """
        Get the total number of stored memories.
        
        Returns:
            Count of memories in the database
        """
        return self.collection.count()


# Example usage
if __name__ == "__main__":
    # Initialize vector store
    store = VectorMemoryStore()
    
    # Store sample memories
    memory1 = "User is preparing for GATE Computer Science exam. Weak topics include Operating Systems and DBMS. Already knows SQL basics."
    memory2 = "User discussed Indian constitutional law and mentioned interest in legal philosophy. Referenced J Sai Deepak's work."
    
    store.store_memory(memory1, metadata={"topics": ["GATE", "CS", "OS", "DBMS"]})
    store.store_memory(memory2, metadata={"topics": ["law", "constitution", "philosophy"]})
    
    # Search for relevant memories
    print("\nSearching for: 'database management'")
    results = store.search_memories("database management", top_k=2)
    for result in results:
        print(f"\nMemory: {result['summary']}")
        print(f"Distance: {result['distance']}")
    
    # Get memory count
    print(f"\nTotal memories stored: {store.get_memory_count()}")
