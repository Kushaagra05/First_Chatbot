"""
Flask API Service for Memory System
Provides REST API endpoints to bridge Node.js backend with Python memory service.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

from memory import MemoryCompressor, VectorMemoryStore, MemoryRetriever
from nlp import EntityExtractor
from services import PromptBuilder

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for Node.js backend

# Configuration
MEMORY_THRESHOLD = int(os.getenv('MEMORY_THRESHOLD', 20))
TOP_K_MEMORIES = int(os.getenv('TOP_K_MEMORIES', 3))

# Lazy initialization - models loaded on first use
_components = {}

def get_components():
    """Lazy load memory components on first use."""
    if not _components:
        _components['compressor'] = MemoryCompressor(api_key=os.getenv('OPENAI_API_KEY'))
        _components['vector_store'] = VectorMemoryStore(persist_directory=os.getenv('CHROMA_DB_PATH', './chroma_db'))
        _components['retriever'] = MemoryRetriever(_components['vector_store'])
        _components['entity_extractor'] = EntityExtractor()
        _components['prompt_builder'] = PromptBuilder()
    return _components


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'memory-api',
        'version': '1.0.0'
    })


@app.route('/api/compress', methods=['POST'])
def compress_conversation():
    """
    Compress conversation history into a summary and store in vector database.
    
    Request Body:
        {
            "conversation": [
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}
            ]
        }
    
    Returns:
        {
            "success": true,
            "summary": "...",
            "memory_id": "...",
            "metadata": {...}
        }
    """
    try:
        data = request.json
        conversation = data.get('conversation', [])
        
        if not conversation:
            return jsonify({
                'success': False,
                'error': 'No conversation provided'
            }), 400
        
        # Get components (lazy load)
        components = get_components()
        
        # Compress conversation
        print(f"Compressing {len(conversation)} messages...")
        summary = components['compressor'].compress_conversation(conversation)
        
        # Extract metadata
        metadata = components['entity_extractor'].extract_metadata_from_conversation(conversation)
        
        # Store in vector database
        memory_id = components['vector_store'].store_memory(
            summary=summary,
            metadata=metadata
        )
        
        print(f"Memory stored with ID: {memory_id}")
        
        return jsonify({
            'success': True,
            'summary': summary,
            'memory_id': memory_id,
            'metadata': metadata
        })
    
    except Exception as e:
        print(f"Error compressing conversation: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/retrieve', methods=['POST'])
def retrieve_memories():
    """
    Retrieve relevant memories for a query.
    
    Request Body:
        {
            "query": "What did we discuss about operating systems?",
            "top_k": 3
        }
    
    Returns:
        {
            "success": true,
            "memories": [
                {
                    "summary": "...",
                    "metadata": {...},
                    "distance": 0.42
                }
            ],
            "count": 3
        }
    """
    try:
        data = request.json
        query = data.get('query', '')
        top_k = data.get('top_k', TOP_K_MEMORIES)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'No query provided'
            }), 400
        
        # Get components (lazy load)
        components = get_components()
        
        # Retrieve relevant memories
        print(f"Retrieving memories for: {query[:50]}...")
        memories = components['retriever'].retrieve_with_metadata(query, top_k=top_k)
        
        return jsonify({
            'success': True,
            'memories': memories,
            'count': len(memories)
        })
    
    except Exception as e:
        print(f"Error retrieving memories: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/build-prompt', methods=['POST'])
def build_enhanced_prompt():
    """
    Build enhanced prompt with memory context.
    
    Request Body:
        {
            "query": "Tell me about operating systems",
            "recent_history": [
                {"role": "user", "content": "..."}
            ],
            "retrieve_memories": true
        }
    
    Returns:
        {
            "success": true,
            "enhanced_prompt": "...",
            "memories_used": 3
        }
    """
    try:
        data = request.json
        query = data.get('query', '')
        recent_history = data.get('recent_history', [])
        should_retrieve = data.get('retrieve_memories', True)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'No query provided'
            }), 400
        
        # Get components (lazy load)
        components = get_components()
        
        # Retrieve memories if requested
        memories = []
        if should_retrieve:
            memories = components['retriever'].retrieve_relevant_memories(query, top_k=TOP_K_MEMORIES)
        
        # Build enhanced prompt
        enhanced_prompt = components['prompt_builder'].build_prompt(
            current_query=query,
            retrieved_memories=memories,
            recent_history=recent_history
        )
        
        return jsonify({
            'success': True,
            'enhanced_prompt': enhanced_prompt,
            'memories_used': len(memories)
        })
    
    except Exception as e:
        print(f"Error building prompt: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """
    Get memory system statistics.
    
    Returns:
        {
            "success": true,
            "total_memories": 10,
            "topics": ["operating systems", "databases", ...],
            "memory_threshold": 20
        }
    """
    try:
        components = get_components()
        stats = components['retriever'].get_memory_statistics()
        stats['memory_threshold'] = MEMORY_THRESHOLD
        stats['top_k_memories'] = TOP_K_MEMORIES
        
        return jsonify({
            'success': True,
            **stats
        })
    
    except Exception as e:
        print(f"Error getting statistics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/clear-memories', methods=['POST'])
def clear_all_memories():
    """
    Clear all memories from vector database (admin function).
    
    Returns:
        {
            "success": true,
            "message": "All memories cleared"
        }
    """
    try:
        components = get_components()
        components['vector_store'].clear_all_memories()
        
        return jsonify({
            'success': True,
            'message': 'All memories cleared successfully'
        })
    
    except Exception as e:
        print(f"Error clearing memories: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/check-threshold', methods=['POST'])
def check_compression_threshold():
    """
    Check if conversation length exceeds threshold.
    
    Request Body:
        {
            "message_count": 25
        }
    
    Returns:
        {
            "should_compress": true,
            "message_count": 25,
            "threshold": 20
        }
    """
    try:
        data = request.json
        message_count = data.get('message_count', 0)
        
        should_compress = message_count >= MEMORY_THRESHOLD
        
        return jsonify({
            'should_compress': should_compress,
            'message_count': message_count,
            'threshold': MEMORY_THRESHOLD
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.getenv('MEMORY_SERVICE_PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("=" * 50)
    print("Memory Service API Starting...")
    print(f"Port: {port}")
    print(f"Memory Threshold: {MEMORY_THRESHOLD} messages")
    print(f"Top-K Retrieval: {TOP_K_MEMORIES} memories")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
