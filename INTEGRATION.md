# Memory System Integration Guide

## Quick Start

### 1. Install Python Memory Service

```bash
cd backend/memory_service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Configure Environment

Create `backend/memory_service/.env`:
```
OPENAI_API_KEY=your_openai_api_key_here
MEMORY_THRESHOLD=20
TOP_K_MEMORIES=3
MEMORY_SERVICE_PORT=5001
CHROMA_DB_PATH=./chroma_db
```

### 3. Start Memory Service

```bash
cd backend/memory_service
python api.py
```

You should see:
```
Memory Service API Starting...
Port: 5001
Memory Threshold: 20 messages
```

### 4. Update Node.js Backend

Add to your `backend/.env`:
```
MEMORY_SERVICE_URL=http://localhost:5001
MEMORY_THRESHOLD=20
TOP_K_MEMORIES=3
```

### 5. Integrate with server.js

Replace your existing chat handler with memory-enhanced version:

```javascript
const memoryService = require('./memoryIntegration');

// Add to your /api/chat endpoint
app.post('/api/chat', async (req, res) => {
  try {
    const { message, sessionId = 'default' } = req.body;
    
    // Process with memory enhancement
    const response = await memoryService.processChatWithMemory(
      sessionId,
      message,
      async (enhancedMessage) => {
        // Your existing OpenAI call
        return await handleOpenAIChat(enhancedMessage);
      }
    );
    
    res.json({ response });
  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Add memory stats endpoint
app.get('/api/memory/stats', async (req, res) => {
  const stats = await memoryService.getMemoryStats();
  res.json(stats);
});

// Add memory clear endpoint (admin)
app.post('/api/memory/clear', async (req, res) => {
  const success = await memoryService.clearAllMemories();
  res.json({ success });
});
```

## How It Works

### Memory Flow

```
User Message
    ↓
Add to History (Node.js)
    ↓
Check Message Count
    ↓
[If > 20 messages]
    ↓
Compress → Python Service
    ↓
    - LLM Summarization
    - Entity Extraction
    - Store in ChromaDB
    ↓
Retrieve Relevant Memories
    ↓
    - Semantic Search
    - Top-K Results
    ↓
Build Enhanced Prompt
    ↓
    - Memory Context
    - Recent History
    - J Sai Deepak Personality
    ↓
Send to OpenAI
    ↓
Assistant Response
```

### Memory Compression

When conversation exceeds 20 messages:
1. **Compress**: Summarize old messages using GPT
2. **Extract**: Identify entities (people, places, topics)
3. **Store**: Save in vector database with embeddings
4. **Keep**: Retain only last 5 messages for context

### Memory Retrieval

For each new query:
1. **Search**: Find 3 most relevant past memories
2. **Rank**: By semantic similarity (cosine distance)
3. **Include**: Add to prompt context

## Testing

### Test 1: Memory Service Health
```bash
curl http://localhost:5001/health
```

Expected:
```json
{
  "status": "healthy",
  "service": "memory-api"
}
```

### Test 2: Compress Conversation
```bash
curl -X POST http://localhost:5001/api/compress \
  -H "Content-Type: application/json" \
  -d '{
    "conversation": [
      {"role": "user", "content": "I am studying DBMS"},
      {"role": "assistant", "content": "Great! DBMS..."}
    ]
  }'
```

### Test 3: Retrieve Memories
```bash
curl -X POST http://localhost:5001/api/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What did we discuss about databases?",
    "top_k": 3
  }'
```

### Test 4: Full Chat Flow

Send 25+ messages to your chatbot. Watch the logs:
```
Compressing 20 messages...
Memory stored: abc123
Retrieved 3 relevant memories
Built enhanced prompt using 3 memories
```

## Frontend Changes (Optional)

Add memory stats display in your UI:

```javascript
// Fetch memory stats
async function getMemoryStats() {
  const response = await fetch(`${API_URL}/api/memory/stats`);
  const stats = await response.json();
  console.log(`Total Memories: ${stats.total_memories}`);
  console.log(`Topics:`, stats.topics);
}
```

## Production Deployment

### Option 1: Same Server
Both Node.js and Python on same machine:
- Node.js: Port 3001
- Python: Port 5001
- Set `MEMORY_SERVICE_URL=http://localhost:5001`

### Option 2: Separate Services
Python on different server:
- Deploy Python service to Render/Heroku
- Update `MEMORY_SERVICE_URL=https://your-memory-service.onrender.com`

### Render Deployment

Create `backend/memory_service/Procfile`:
```
web: gunicorn -w 4 -b 0.0.0.0:$PORT api:app
```

Add to `requirements.txt`:
```
gunicorn==21.2.0
```

Deploy:
1. Create new Web Service on Render
2. Point to `backend/memory_service` directory
3. Set environment variables (OPENAI_API_KEY, etc.)
4. Update Node.js backend with new URL

## Troubleshooting

### Memory Service Won't Start

```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check port availability
netstat -an | findstr 5001
```

### ChromaDB Errors

```bash
# Clear database
rm -rf chroma_db

# Restart service
python api.py
```

### Node.js Can't Connect

```bash
# Test connectivity
curl http://localhost:5001/health

# Check firewall/antivirus blocking port 5001
```

### Memory Not Compressing

Check logs:
```javascript
console.log('Message count:', session.messages.length);
console.log('Threshold:', MEMORY_THRESHOLD);
```

### Slow Performance

- Reduce `TOP_K_MEMORIES` to 2
- Increase `MEMORY_THRESHOLD` to 30
- Use smaller embedding model

## Monitoring

Add logging to track memory usage:

```javascript
setInterval(async () => {
  const stats = await memoryService.getMemoryStats();
  console.log('=== MEMORY STATS ===');
  console.log('Total memories:', stats.total_memories);
  console.log('Active sessions:', conversationSessions.size);
}, 60000); // Every minute
```

## Next Steps

1. ✅ Start Python memory service
2. ✅ Test all API endpoints
3. ✅ Integrate with Node.js backend
4. Test with 30+ message conversation
5. Deploy to production
6. Monitor memory compression and retrieval

## Support

- **Memory service not responding**: Check if Python process is running
- **Compression not working**: Verify OPENAI_API_KEY in `.env`
- **ChromaDB issues**: Delete `chroma_db` folder and restart
- **Integration errors**: Check `MEMORY_SERVICE_URL` in both services

Your chatbot now has long-term memory! 🧠✨
