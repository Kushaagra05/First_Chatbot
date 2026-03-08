"""
Entity Extraction Module
Extracts named entities and key topics from conversation text using spaCy.
"""

import spacy
from typing import List, Dict, Set
from collections import Counter

class EntityExtractor:
    """
    Extracts entities, topics, and key concepts from conversation text
    to enrich memory metadata.
    """
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize spaCy NLP model for entity extraction.
        
        Args:
            model_name: spaCy model to use
            
        Note:
            If model not found, download with:
            python -m spacy download en_core_web_sm
        """
        try:
            self.nlp = spacy.load(model_name)
            print(f"Loaded spaCy model: {model_name}")
        except OSError:
            print(f"Model '{model_name}' not found. Downloading...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", model_name])
            self.nlp = spacy.load(model_name)
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text.
        
        Args:
            text: Input text to process
            
        Returns:
            Dict with entity types as keys and entity lists as values
            
        Example:
            >>> extractor = EntityExtractor()
            >>> entities = extractor.extract_entities("I'm studying at MIT for GATE exam")
            >>> print(entities)
            {'ORG': ['MIT'], 'EVENT': ['GATE']}
        """
        doc = self.nlp(text)
        
        entities_by_type = {}
        for ent in doc.ents:
            if ent.label_ not in entities_by_type:
                entities_by_type[ent.label_] = []
            entities_by_type[ent.label_].append(ent.text)
        
        # Remove duplicates while preserving order
        for entity_type in entities_by_type:
            seen = set()
            unique_entities = []
            for ent in entities_by_type[entity_type]:
                if ent not in seen:
                    seen.add(ent)
                    unique_entities.append(ent)
            entities_by_type[entity_type] = unique_entities
        
        return entities_by_type
    
    def extract_key_topics(self, text: str, top_n: int = 5) -> List[str]:
        """
        Extract key topics/concepts using noun chunks and named entities.
        
        Args:
            text: Input text to process
            top_n: Number of top topics to return
            
        Returns:
            List of key topics/concepts
            
        Example:
            >>> topics = extractor.extract_key_topics("I need help with operating systems")
            >>> print(topics)
            ['operating systems', 'help']
        """
        doc = self.nlp(text.lower())
        
        # Collect noun chunks (phrases)
        topics = []
        for chunk in doc.noun_chunks:
            # Filter out very common words
            if chunk.root.pos_ in ['NOUN', 'PROPN'] and not chunk.root.is_stop:
                topics.append(chunk.text)
        
        # Also add named entities as topics
        for ent in doc.ents:
            topics.append(ent.text.lower())
        
        # Count frequency and return top N
        topic_counts = Counter(topics)
        top_topics = [topic for topic, count in topic_counts.most_common(top_n)]
        
        return top_topics
    
    def extract_metadata_from_conversation(self, conversation: List[Dict[str, str]]) -> Dict:
        """
        Extract comprehensive metadata from conversation history.
        
        Args:
            conversation: List of message dicts with 'role' and 'content'
            
        Returns:
            Dict containing entities, topics, and other metadata
            
        Example:
            >>> conversation = [
            ...     {"role": "user", "content": "I'm studying DBMS at IIT Delhi"}
            ... ]
            >>> metadata = extractor.extract_metadata_from_conversation(conversation)
            >>> print(metadata['topics'])
            ['DBMS', 'IIT Delhi']
        """
        # Combine all conversation text
        full_text = " ".join([
            msg['content'] for msg in conversation
            if msg['role'] == 'user'  # Focus on user messages
        ])
        
        # Extract entities
        entities = self.extract_entities(full_text)
        
        # Extract topics
        topics = self.extract_key_topics(full_text, top_n=10)
        
        # Identify important concepts
        important_concepts = self._identify_concepts(full_text)
        
        metadata = {
            'entities': entities,
            'topics': topics,
            'concepts': important_concepts,
            'message_count': len(conversation)
        }
        
        return metadata
    
    def _identify_concepts(self, text: str) -> List[str]:
        """
        Identify important technical or domain-specific concepts.
        
        Args:
            text: Input text
            
        Returns:
            List of identified concepts
        """
        doc = self.nlp(text.lower())
        
        concepts = []
        
        # Look for capitalized terms and noun phrases
        for token in doc:
            # Technical terms are often capitalized or compound nouns
            if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop:
                if len(token.text) > 3:  # Filter short words
                    concepts.append(token.text)
        
        # Return unique concepts
        return list(set(concepts))
    
    def enrich_summary_with_entities(self, summary: str) -> Dict:
        """
        Enrich a memory summary with extracted entities and topics.
        
        Args:
            summary: Memory summary text
            
        Returns:
            Dict with summary and enrichment metadata
        """
        entities = self.extract_entities(summary)
        topics = self.extract_key_topics(summary)
        
        return {
            'summary': summary,
            'entities': entities,
            'topics': topics
        }


# Example usage
if __name__ == "__main__":
    # Initialize extractor
    extractor = EntityExtractor()
    
    # Test text
    test_text = """
    I'm preparing for the GATE Computer Science exam at IIT Delhi. 
    I'm particularly weak in Operating Systems and Database Management Systems.
    I've been reading about Indian constitutional law and J Sai Deepak's books on legal philosophy.
    """
    
    print("=== ENTITY EXTRACTION ===")
    entities = extractor.extract_entities(test_text)
    for entity_type, entity_list in entities.items():
        print(f"{entity_type}: {entity_list}")
    
    print("\n=== KEY TOPICS ===")
    topics = extractor.extract_key_topics(test_text, top_n=8)
    print(topics)
    
    print("\n=== CONVERSATION METADATA ===")
    conversation = [
        {"role": "user", "content": "I'm studying Computer Science at MIT"},
        {"role": "assistant", "content": "That's great!"},
        {"role": "user", "content": "I need help with algorithms and data structures"}
    ]
    metadata = extractor.extract_metadata_from_conversation(conversation)
    print(f"Topics: {metadata['topics']}")
    print(f"Entities: {metadata['entities']}")
