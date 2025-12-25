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

const model = genAI.getGenerativeModel({ model: 'gemini-pro' });

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


// Multi-agent helper function
async function callAgent(agentType, input) {
  const provider = process.env.API_PROVIDER;
  
  const prompts = {
    researcher: `You are the Researcher Agent.
Your job is to gather comprehensive information about:

TOPIC: ${input}

Provide:
- Definitions and background
- Key concepts and components
- Real-world applications
- Pros & cons
- Current trends and future outlook

Return the info in clear bullet points.`,

    summarizer: `You are the Summarizer Agent.
Take the following research and create a concise summary.

Research:
${input}

Return:
- Key points (3-5 main ideas)
- Simplified explanation
- Most important facts`,

    critic: `You are the Critic Agent.
Analyze this summary and identify gaps or improvements needed.

Summary:
${input}

Check for:
- Missing key information
- Vague or unclear explanations
- Areas needing more detail
- Potential inaccuracies

Return your critique as bullet points.`,

    writer: `You are the Writer Agent.
Create a well-structured report on:

TOPIC: ${input.topic}

Using this summary:
${input.summary}

And addressing these critique points:
${input.critique}

Format the report with:
- Clear sections with headers
- Professional tone
- Easy-to-read structure
- Bullet points where appropriate`
  };

  const prompt = prompts[agentType];
  
  if (provider === 'gemini') {
    const model = genAI.getGenerativeModel({ model: 'gemini-pro' });
    const result = await model.generateContent(prompt);
    const response = await result.response;
    return response.text();
  } else if (provider === 'openai') {
    const completion = await openai.chat.completions.create({
      model: "gpt-3.5-turbo",
      messages: [{ role: 'user', content: prompt }]
    });
    return completion.choices[0].message.content;
  }
}

// Research endpoint - multi-agent workflow
app.post('/api/research', async (req, res) => {
  try {
    const { topic } = req.body;

    if (!topic) {
      return res.status(400).json({ error: 'Topic is required' });
    }

    console.log(`\n=== Research Request: ${topic} ===`);

    // Step 1: Research
    console.log('Researching...');
    const research = await callAgent('researcher', topic);

    // Step 2: Summarize
    console.log('Summarizing...');
    const summary = await callAgent('summarizer', research);

    // Step 3: Critique
    console.log('Critiquing...');
    const critique = await callAgent('critic', summary);

    // Step 4: Write final report
    console.log('Writing final report...');
    const finalReport = await callAgent('writer', { topic, summary, critique });

    res.json({
      report: finalReport,
      metadata: {
        research,
        summary,
        critique
      },
      provider: process.env.API_PROVIDER,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Research error:', error);
    res.status(500).json({
      error: 'Failed to generate research report',
      details: error.message
    });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`API Provider: ${process.env.API_PROVIDER || 'not set'}`);
});
