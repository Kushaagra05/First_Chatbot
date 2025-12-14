import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { GoogleGenerativeAI } from '@google/generative-ai';
import OpenAI from 'openai';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Initialize AI clients
let genAI, openai;

if (process.env.API_PROVIDER === 'gemini' && process.env.GEMINI_API_KEY) {
  genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
}

if (process.env.API_PROVIDER === 'openai' && process.env.OPENAI_API_KEY) {
  openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
  });
}

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    provider: process.env.API_PROVIDER,
    timestamp: new Date().toISOString()
  });
});

// Chat endpoint
app.post('/api/chat', async (req, res) => {
  try {
    const { message, conversationHistory = [] } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    const provider = process.env.API_PROVIDER;
    let reply;

    if (provider === 'gemini') {
      reply = await handleGeminiChat(message, conversationHistory);
    } else if (provider === 'openai') {
      reply = await handleOpenAIChat(message, conversationHistory);
    } else {
      return res.status(500).json({ error: 'No API provider configured' });
    }

    res.json({
      reply,
      provider,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({
      error: 'Failed to process chat message',
      details: error.message
    });
  }
});

// Gemini chat handler
async function handleGeminiChat(message, conversationHistory) {
  if (!genAI) {
    throw new Error('Gemini API not configured');
  }

const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash-latest' });

  // Build conversation context
  let prompt = '';
  if (conversationHistory.length > 0) {
    conversationHistory.forEach(msg => {
      prompt += `${msg.role === 'user' ? 'User' : 'Assistant'}: ${msg.content}\n`;
    });
  }
  prompt += `User: ${message}\nAssistant:`;

  const result = await model.generateContent(prompt);
  const response = await result.response;
  return response.text();
}

// OpenAI chat handler
async function handleOpenAIChat(message, conversationHistory) {
  if (!openai) {
    throw new Error('OpenAI API not configured');
  }

  const messages = conversationHistory.map(m => ({
    role: m.role,
    content: m.content
  }));

  messages.push({
    role: 'user',
    content: message
  });

  const completion = await openai.chat.completions.create({
    model: "gpt-3.5-turbo",
    messages: messages
  });

  return completion.choices[0].message.content;
}


// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`API Provider: ${process.env.API_PROVIDER || 'not set'}`);
});
