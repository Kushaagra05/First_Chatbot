# Memory Service Setup Instructions

## Overview
This Python memory service adds conversational memory compression and retrieval to your J Sai Deepak chatbot.

## Prerequisites
- Python 3.8 or higher
- pip package manager
- OpenAI API key (same one used in Node.js backend)

## Installation Steps

### 1. Navigate to Memory Service Directory
```bash
cd backend/memory_service
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download spaCy Language Model
```bash
python -m spacy download en_core_web_sm
```

### 5. Configure Environment Variables
```bash
# Copy example env file
copy .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_api_key_here
```

### 6. Test the Installation
```bash
# Test memory compressor
python memory/compressor.py

# Test vector store
python memory/vector_store.py

# Test entity extractor
python nlp/entity_extractor.py
```

### 7. Start the Memory Service API
```bash
python api.py
```

The service will start on `http://localhost:5001`

## API Endpoints

### Health Check
```
GET /health
```

### Compress Conversation
```
POST /api/compress
Body: {
  "conversation": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

### Retrieve Memories
```
POST /api/retrieve
Body: {
  "query": "What did we discuss?",
  "top_k": 3
}
```

### Build Enhanced Prompt
```
POST /api/build-prompt
Body: {
  "query": "Tell me about X",
  "recent_history": [...],
  "retrieve_memories": true
}
```

### Get Statistics
```
GET /api/stats
```

### Check Compression Threshold
```
POST /api/check-threshold
Body: {
  "message_count": 25
}
```

## Integration with Node.js Backend

Add this to your `backend/server.js`:

```javascript
const axios = require('axios');

const MEMORY_SERVICE_URL = 'http://localhost:5001';

// Check if compression needed
async function checkCompressionThreshold(messageCount) {
  try {
    const response = await axios.post(`${MEMORY_SERVICE_URL}/api/check-threshold`, {
      message_count: messageCount
    });
    return response.data.should_compress;
  } catch (error) {
    console.error('Memory service error:', error.message);
    return false;
  }
}

// Compress and store conversation
async function compressConversation(conversation) {
  try {
    const response = await axios.post(`${MEMORY_SERVICE_URL}/api/compress`, {
      conversation
    });
    return response.data;
  } catch (error) {
    console.error('Compression error:', error.message);
    return null;
  }
}

// Retrieve relevant memories
async function retrieveMemories(query, topK = 3) {
  try {
    const response = await axios.post(`${MEMORY_SERVICE_URL}/api/retrieve`, {
      query,
      top_k: topK
    });
    return response.data.memories || [];
  } catch (error) {
    console.error('Retrieval error:', error.message);
    return [];
  }
}

// Build enhanced prompt with memory context
async function buildEnhancedPrompt(query, recentHistory) {
  try {
    const response = await axios.post(`${MEMORY_SERVICE_URL}/api/build-prompt`, {
      query,
      recent_history: recentHistory,
      retrieve_memories: true
    });
    return response.data.enhanced_prompt;
  } catch (error) {
    console.error('Prompt building error:', error.message);
    return query; // Fallback to original query
  }
}
```

## Architecture Flow

1. **User sends message** → Node.js backend receives request
2. **Check message count** → If > 20, compress old messages
3. **Retrieve memories** → Python service searches vector DB
4. **Build enhanced prompt** → Combine memories + recent context
5. **Send to OpenAI** → Get response with full context
6. **Store response** → Add to conversation history

## Memory Threshold Configuration

Edit `.env`:
```
MEMORY_THRESHOLD=20        # Compress after N messages
TOP_K_MEMORIES=3          # Retrieve N relevant memories
MEMORY_SERVICE_PORT=5001  # Python service port
```

## Troubleshooting

### Port Already in Use
```bash
# Change port in .env
MEMORY_SERVICE_PORT=5002
```

### ChromaDB Issues
```bash
# Clear database
rm -rf chroma_db
```

### spaCy Model Not Found
```bash
python -m spacy download en_core_web_sm
```

### OpenAI API Errors
Check that your `.env` has the correct API key:
```
OPENAI_API_KEY=sk-...
```

## Production Deployment

For deployment on Render/Heroku:

1. Add `Procfile`:
```
web: python api.py
```

2. Set environment variables in hosting platform
3. Use production-grade WSGI server:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:$PORT api:app
```

## Development vs Production

**Development:**
- Run both services locally (Node.js on 3001, Python on 5001)
- Use localhost URLs

**Production:**
- Deploy Python service separately or alongside Node.js
- Update MEMORY_SERVICE_URL to production URL
- Enable HTTPS

## Next Steps

1. ✅ Install and test memory service
2. ✅ Integrate with Node.js backend
3. Test compression and retrieval
4. Deploy to production
5. Monitor memory usage and performance

## Support

For issues or questions about the memory system:
- Check logs in terminal
- Verify all dependencies installed
- Ensure OpenAI API key is valid
- Test individual components first before integration
