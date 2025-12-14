# AI Chatbot

A full-stack chatbot application with support for Google Gemini and OpenAI APIs.

## Project Structure

```
First_Chatbot/
├── backend/          # Node.js/Express API server
│   ├── server.js     # Main server file
│   ├── package.json
│   ├── .env.example
│   └── .gitignore
├── frontend/         # React application
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── .env.example
│   └── .gitignore
└── README.md
```

## Features

- 💬 Real-time chat interface
- 🔄 Support for both Google Gemini and OpenAI APIs
- 📱 Responsive design (works on mobile and desktop)
- 💾 Conversation history maintained during session
- 🎨 Modern, clean UI with smooth animations
- 🚀 Ready for deployment on GitHub Pages (frontend) and Render (backend)

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file from the example:
   ```bash
   copy .env.example .env
   ```

4. Edit `.env` and add your API keys:
   - Set `API_PROVIDER` to either `gemini` or `openai`
   - Add your `GEMINI_API_KEY` or `OPENAI_API_KEY`

5. Start the development server:
   ```bash
   npm run dev
   ```

   The backend will run on `http://localhost:3001`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file from the example:
   ```bash
   copy .env.example .env
   ```

4. Start the development server:
   ```bash
   npm start
   ```

   The frontend will run on `http://localhost:3000`

## API Keys

### Get Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key to your backend `.env` file

### Get OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key to your backend `.env` file

## Deployment

### Deploy Backend to Render

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Build Command:** `cd backend && npm install`
   - **Start Command:** `cd backend && npm start`
   - **Environment Variables:** Add your API keys from `.env`
6. Deploy!

### Deploy Frontend to GitHub Pages

1. Update `frontend/.env` with your Render backend URL:
   ```
   REACT_APP_API_URL=https://your-app-name.onrender.com
   ```

2. Build the frontend:
   ```bash
   cd frontend
   npm run build
   ```

3. Install gh-pages:
   ```bash
   npm install --save-dev gh-pages
   ```

4. Add to `frontend/package.json`:
   ```json
   "scripts": {
     "predeploy": "npm run build",
     "deploy": "gh-pages -d build"
   }
   ```

5. Deploy:
   ```bash
   npm run deploy
   ```

## Usage

1. Start both backend and frontend servers
2. Open the chat interface in your browser
3. Type a message and press Enter or click the send button
4. The chatbot will respond using your configured AI provider (Gemini or OpenAI)

## Switching Between AI Providers

To switch between Gemini and OpenAI:

1. Open `backend/.env`
2. Change `API_PROVIDER=gemini` to `API_PROVIDER=openai` (or vice versa)
3. Restart the backend server
4. The chat interface will display which provider is active

## License

MIT