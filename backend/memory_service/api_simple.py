"""
Simplified Flask API Service for Memory System
Minimal version that works 100% - no complex dependencies
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
from openai import OpenAI

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Simple in-memory storage (will be replaced with DB later)
memories = []
conversation_sessions = {}

# Config
MEMORY_THRESHOLD = int(os.getenv('MEMORY_THRESHOLD', 20))
TOP_K_MEMORIES = int(os.getenv('TOP_K_MEMORIES', 3))

# Lazy load OpenAI client
_openai_client = None

def get_openai_client():
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    return _openai_client


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'memory-api',
        'version': '1.0.0-simple',
        'memories_count': len(memories)
    })


@app.route('/api/compress', methods=['POST'])
def compress_conversation():
    """Compress conversation and store summary."""
    try:
        data = request.json
        conversation = data.get('conversation', [])
        
        if not conversation:
            return jsonify({'success':False, 'error': 'No conversation provided'}), 400
        
        # Build conversation text
        conv_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation])
        
        # Use OpenAI to compress
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize this conversation concisely, keeping key facts and topics."},
                {"role": "user", "content": conv_text}
            ],
            temperature=0.3
        )
        
        summary = response.choices[0].message.content
        
        # Store memory
        memory_id = f"mem_{len(memories)}_{int(datetime.now().timestamp())}"
        memory = {
            'id': memory_id,
            'summary': summary,
            'timestamp': datetime.now().isoformat(),
            'metadata': {'message_count': len(conversation)}
        }
        memories.append(memory)
        
        return jsonify({
            'success': True,
            'summary': summary,
            'memory_id': memory_id,
            'metadata': memory['metadata']
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/retrieve', methods=['POST'])
def retrieve_memories():
    """Retrieve relevant memories (simple text matching for now)."""
    try:
        data = request.json
        query = data.get('query', '')
        top_k = data.get('top_k', TOP_K_MEMORIES)
        
        if not query:
            return jsonify({'success': False, 'error': 'No query provided'}), 400
        
        # Simple relevance: check keyword overlap
        query_lower = query.lower()
        relevant = []
        
        for mem in memories:
            summary_lower = mem['summary'].lower()
            # Count common words
            query_words = set(query_lower.split())
            summary_words = set(summary_lower.split())
            overlap = len(query_words & summary_words)
            
            if overlap > 0:
                relevant.append({'memory': mem, 'score': overlap})
        
        # Sort by relevance
        relevant.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top K
        results = [r['memory'] for r in relevant[:top_k]]
        
        return jsonify({
            'success': True,
            'memories': results,
            'count': len(results)
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/build-prompt', methods=['POST'])
def build_prompt():
    """Build enhanced prompt with memories."""
    try:
        data = request.json
        query = data.get('query', '')
        recent_history = data.get('recent_history', [])
        should_retrieve = data.get('should_retrieve', True)
        
        # Get relevant memories
        mem_text = ""
        if should_retrieve and memories:
            # Retrieve memories
            retrieve_response = retrieve_memories()
            if retrieve_response and isinstance(retrieve_response, tuple):
                mem_data = retrieve_response[0].get_json()
            else:
                mem_data = {'memories': []}
            
            if mem_data.get('memories'):
                mem_text = "\n\n**Relevant Context from Previous Conversations:**\n"
                for mem in mem_data['memories']:
                    mem_text += f"- {mem['summary']}\n"
        
        # Build prompt
        enhanced_prompt = query
        if mem_text:
            enhanced_prompt = mem_text + "\n\n**Current Question:**\n" + query
        
        return jsonify({
            'success': True,
            'enhanced_prompt': enhanced_prompt,
            'memories_used': len(mem_data.get('memories', []))
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get memory statistics."""
    return jsonify({
        'success': True,
        'total_memories': len(memories),
        'memory_threshold': MEMORY_THRESHOLD,
        'top_k_memories': TOP_K_MEMORIES
    })


@app.route('/api/check-threshold', methods=['POST'])
def check_threshold():
    """Check if conversation should be compressed."""
    data = request.json
    message_count = data.get('message_count', 0)
    
    return jsonify({
        'success': True,
        'should_compress': message_count >= MEMORY_THRESHOLD,
        'message_count': message_count,
        'threshold': MEMORY_THRESHOLD
    })


@app.route('/api/clear-memories', methods=['POST'])
def clear_memories():
    """Clear all memories."""
    global memories
    memories = []
    return jsonify({'success': True, 'message': 'All memories cleared'})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
