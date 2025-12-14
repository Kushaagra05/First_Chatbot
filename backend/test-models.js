import { GoogleGenerativeAI } from '@google/generative-ai';
import dotenv from 'dotenv';

dotenv.config();

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

async function listModels() {
  try {
    console.log('Fetching available models...\n');
    
    // Try the new API method
    const models = await genAI.listModels();
    
    console.log('Available models:');
    for await (const model of models) {
      console.log(`- ${model.name}`);
      if (model.supportedGenerationMethods?.includes('generateContent')) {
        console.log('  ✓ Supports generateContent');
      }
    }
  } catch (error) {
    console.error('Error:', error.message);
    
    // Try testing specific models
    console.log('\nTrying specific models...\n');
    const testModels = [
      'gemini-1.5-pro',
      'gemini-1.5-flash',
      'gemini-pro',
      'gemini-2.0-flash',
      'models/gemini-1.5-pro',
      'models/gemini-1.5-flash'
    ];
    
    for (const modelName of testModels) {
      try {
        const model = genAI.getGenerativeModel({ model: modelName });
        const result = await model.generateContent('test');
        console.log(`✓ ${modelName} - WORKS!`);
      } catch (err) {
        console.log(`✗ ${modelName} - ${err.message.substring(0, 80)}`);
      }
    }
  }
}

listModels();
