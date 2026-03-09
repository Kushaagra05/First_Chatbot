/**
 * Memory Service Integration Module
 * Connects Node.js backend with Python memory service
 */

import axios from 'axios';

// Configuration
const MEMORY_SERVICE_URL = process.env.MEMORY_SERVICE_URL || 'http://localhost:5001';
const MEMORY_THRESHOLD = parseInt(process.env.MEMORY_THRESHOLD) || 20;
const TOP_K_MEMORIES = parseInt(process.env.TOP_K_MEMORIES) || 3;

// Track conversation history per session
const conversationSessions = new Map();

/**
 * Check if memory service is available
 */
async function checkMemoryServiceHealth() {
  try {
    const response = await axios.get(`${MEMORY_SERVICE_URL}/health`, { timeout: 5000 });
    return response.data.status === 'healthy';
  } catch (error) {
    console.warn('Memory service not available:', error.message);
    return false;
  }
}

/**
 * Get or create conversation session
 */
function getConversationSession(sessionId = 'default') {
  if (!conversationSessions.has(sessionId)) {
    conversationSessions.set(sessionId, {
      messages: [],
      lastCompression: Date.now()
    });
  }
  return conversationSessions.get(sessionId);
}

/**
 * Add message to conversation history
 */
function addMessage(sessionId, role, content) {
  const session = getConversationSession(sessionId);
  session.messages.push({ role, content, timestamp: Date.now() });
  return session.messages.length;
}

/**
 * Check if conversation should be compressed
 */
async function shouldCompressConversation(sessionId) {
  const session = getConversationSession(sessionId);
  const messageCount = session.messages.length;
  
  // Check local threshold first
  if (messageCount < MEMORY_THRESHOLD) {
    return false;
  }
  
  // Verify with memory service
  try {
    const response = await axios.post(`${MEMORY_SERVICE_URL}/api/check-threshold`, {
      message_count: messageCount
    }, { timeout: 3000 });
    
    return response.data.should_compress;
  } catch (error) {
    console.error('Threshold check error:', error.message);
    // Fallback to local check
    return messageCount >= MEMORY_THRESHOLD;
  }
}

/**
 * Compress conversation and store as memory
 */
async function compressAndStoreConversation(sessionId) {
  const session = getConversationSession(sessionId);
  
  if (session.messages.length === 0) {
    console.log('No messages to compress');
    return null;
  }
  
  try {
    console.log(`Compressing ${session.messages.length} messages...`);
    
    const response = await axios.post(`${MEMORY_SERVICE_URL}/api/compress`, {
      conversation: session.messages
    }, { timeout: 30000 }); // 30 second timeout for compression
    
    if (response.data.success) {
      console.log('Memory stored:', response.data.memory_id);
      console.log('Summary:', response.data.summary.substring(0, 100) + '...');
      
      // Clear old messages, keep only recent N
      const recentCount = 5;
      session.messages = session.messages.slice(-recentCount);
      session.lastCompression = Date.now();
      
      return response.data;
    }
    
    return null;
  } catch (error) {
    console.error('Compression error:', error.message);
    return null;
  }
}

/**
 * Retrieve relevant memories for a query
 */
async function retrieveRelevantMemories(query, topK = TOP_K_MEMORIES) {
  try {
    const response = await axios.post(`${MEMORY_SERVICE_URL}/api/retrieve`, {
      query,
      top_k: topK
    }, { timeout: 10000 });
    
    if (response.data.success) {
      console.log(`Retrieved ${response.data.count} relevant memories`);
      return response.data.memories;
    }
    
    return [];
  } catch (error) {
    console.error('Memory retrieval error:', error.message);
    return [];
  }
}

/**
 * Build enhanced prompt with memory context
 */
async function buildEnhancedPrompt(sessionId, currentQuery) {
  const session = getConversationSession(sessionId);
  
  // Get recent conversation history (last 5 messages)
  const recentHistory = session.messages.slice(-5);
  
  try {
    const response = await axios.post(`${MEMORY_SERVICE_URL}/api/build-prompt`, {
      query: currentQuery,
      recent_history: recentHistory,
      retrieve_memories: true
    }, { timeout: 10000 });
    
    if (response.data.success) {
      console.log(`Built enhanced prompt using ${response.data.memories_used} memories`);
      return response.data.enhanced_prompt;
    }
    
    // Fallback to simple prompt
    return currentQuery;
  } catch (error) {
    console.error('Prompt building error:', error.message);
    return currentQuery;
  }
}

/**
 * Get memory system statistics
 */
async function getMemoryStats() {
  try {
    const response = await axios.get(`${MEMORY_SERVICE_URL}/api/stats`, { timeout: 5000 });
    return response.data;
  } catch (error) {
    console.error('Stats retrieval error:', error.message);
    return null;
  }
}

/**
 * Process chat with memory enhancement
 * Main integration function to use in your chat endpoint
 */
async function processChatWithMemory(sessionId, userMessage, openaiHandler) {
  try {
    // 1. Add user message to history
    addMessage(sessionId, 'user', userMessage);
    
    // 2. Check if memory service is available
    const serviceAvailable = await checkMemoryServiceHealth();
    
    if (!serviceAvailable) {
      console.warn('Processing without memory enhancement');
      // Fallback: use normal chat without memory
      const response = await openaiHandler(userMessage);
      addMessage(sessionId, 'assistant', response);
      return response;
    }
    
    // 3. Check if we need to compress
    const shouldCompress = await shouldCompressConversation(sessionId);
    if (shouldCompress) {
      console.log('Compressing conversation...');
      await compressAndStoreConversation(sessionId);
    }
    
    // 4. Build enhanced prompt with memories
    const enhancedPrompt = await buildEnhancedPrompt(sessionId, userMessage);
    
    // 5. Send to OpenAI with enhanced context
    const response = await openaiHandler(enhancedPrompt);
    
    // 6. Add assistant response to history
    addMessage(sessionId, 'assistant', response);
    
    return response;
    
  } catch (error) {
    console.error('Memory processing error:', error.message);
    // Fallback to normal chat
    const response = await openaiHandler(userMessage);
    addMessage(sessionId, 'assistant', response);
    return response;
  }
}

/**
 * Clear all memories (admin function)
 */
async function clearAllMemories() {
  try {
    const response = await axios.post(`${MEMORY_SERVICE_URL}/api/clear-memories`, {}, { timeout: 5000 });
    return response.data.success;
  } catch (error) {
    console.error('Clear memories error:', error.message);
    return false;
  }
}

/**
 * Clear session history
 */
function clearSession(sessionId) {
  conversationSessions.delete(sessionId);
}

export {
  checkMemoryServiceHealth,
  addMessage,
  shouldCompressConversation,
  compressAndStoreConversation,
  retrieveRelevantMemories,
  buildEnhancedPrompt,
  getMemoryStats,
  processChatWithMemory,
  clearAllMemories,
  clearSession,
  MEMORY_SERVICE_URL
};
