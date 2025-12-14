import { GoogleGenerativeAI } from '@google/generative-ai';
import dotenv from 'dotenv';

dotenv.config();

console.log('API Key:', process.env.GEMINI_API_KEY ? 'Found (length: ' + process.env.GEMINI_API_KEY.length + ')' : 'NOT FOUND');
console.log('Testing connection...\n');

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

async function testSimple() {
  try {
    const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
    console.log('Sending test prompt...');
    const result = await model.generateContent('Say hello');
    const response = await result.response;
    console.log('\n✓ SUCCESS! Response:', response.text());
  } catch (error) {
    console.log('\n✗ ERROR:');
    console.log('Status:', error.status);
    console.log('Message:', error.message);
    console.log('\nFull error:', JSON.stringify(error, null, 2));
  }
}

testSimple();
