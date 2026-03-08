"""
Entity Extraction Module
Extracts named entities and key topics from conversation text using OpenAI.
Python 3.14 compatible version (no spaCy dependency).
"""

import re
import os
from typing import List, Dict
from collections import Counter
from openai import OpenAI

class EntityExtractor:
    """
    Extracts entities, topics, and key concepts from conversation text
    to enrich memory metadata using OpenAI API.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize entity extractor with OpenAI API.
        
        Args:
            api_key: OpenAI API key (optional, will use env var if not provided)
        """
        self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        print("Entity extractor initialized with OpenAI API")
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text using OpenAI.
        
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
        try:
            prompt = f"""Extract named entities from this text and categorize them.

Text: {text}

Return ONLY a JSON object with entity types as keys and lists of entities as values.
Use these categories: PERSON, ORG, GPE (locations), DATE, EVENT, TOPIC

Example format: {{"ORG": ["MIT", "Google"], "EVENT": ["GATE"], "TOPIC": ["Machine Learning"]}}

JSON:"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            result = response.choices[0].message.content.strip()
            # Parse JSON response
            import json
            entities_by_type = json.loads(OpenAI.
        
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
        try:
            prompt = f"""Extract the main topics and key concepts from this text.

Text: {text}

Return ONLY a JSON array of the top {top_n} topics/concepts.
Example: ["operating systems", "database management", "algorithms"]

JSON array:"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            result = response.choices[0].message.content.strip()
            import json
            topics = json.loads(result)
            return topics[:top_n]
            
        except Exception as e:
            print(f"Topic extraction error: {e}")
            # Fallback: simple word frequency
            return self._simple_topic_extraction(text, top_n)pend(chunk.text)
        
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
         simple_entity_extraction(self, text: str) -> Dict[str, List[str]]:
        """
        Fallback: Simple pattern-based entity extraction.
        """
        entities = {
            'TOPIC': [],
            'ORG': []
        }
        
        # Extract capitalized words as potential entities
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        entities['ORG'] = list(set(words))
        
        return entities
    
    def _simple_topic_extraction(self, text: str, top_n: int) -> List[str]:
        """
        Fallback: Simple word frequency based topic extraction.
        """
        # Remove common words and extract nouns
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        stopwords = {'this', 'that', 'with', 'from', 'have', 'been', 'were', 'their'}
        words = [w for w in words if w not in stopwords]
        
        word_counts = Counter(words)
        return [word for word, _ in word_counts.most_common(top_n)]
    
    def _identify_concepts(self, text: str) -> List[str]:
        """
        Identify important technical or domain-specific concepts.
        
        Args:
            text: Input text
            
        Returns:
            List of identified concepts
        """
        # Extract multi-word technical terms and capitalized words
        concepts = []
        
        # Find capitalized multi-word terms
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        concepts.extend(capitalized)
        
        # Find technical abbreviations (2-5 uppercase letters)
        abbreviations = re.findall(r'\b[A-Z]{2,5}\b', text)
        concepts.extend(abbreviations)
        
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
    # Initialize extractor (requires OPENAI_API_KEY in environment)
    extractor = EntityExtractor()
    
    # Test text
    test_text = """
    I'm preparing for the GATE Computer Science exam at IIT Delhi. 
    I'm particularly weak in Operating Systems and Database Management Systems.
    I've been reading about Indian constitutional law.
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
