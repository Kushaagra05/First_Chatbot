# Memory Service - Production Deployment Guide

## Deploy to Render (Step-by-Step)

### Step 1: Prepare for Deployment

Your memory service is ready in GitHub at:
`backend/memory_service/`

✅ All files are committed
✅ Python 3.14 compatible
✅ Requirements.txt ready
✅ Procfile configured

### Step 2: Create Render Web Service

1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `Kushaagra05/First_Chatbot`
4. Configure the service:

**Service Settings:**
```
Name: first-chatbot-memory-service
Region: Singapore (or closest to you)
Branch: main
Root Directory: backend/memory_service
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn -w 2 -b 0.0.0.0:$PORT --timeout 120 api:app
Instance Type: Free
```

### Step 3: Set Environment Variables

In Render dashboard, add these environment variables:

```
OPENAI_API_KEY = your_openai_api_key_here
MEMORY_THRESHOLD = 20
TOP_K_MEMORIES = 3
MEMORY_SERVICE_PORT = 5001
FLASK_DEBUG = False
```

### Step 4: Deploy

Click **"Create Web Service"**

Render will:
- Clone your repo
- Install dependencies
- Start the Flask API
- Give you a URL like: `https://first-chatbot-memory-service.onrender.com`

⏱️ **Deployment takes 5-10 minutes**

### Step 5: Verify Deployment

Once deployed, test the health endpoint:
```bash
curl https://your-memory-service.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "memory-api",
  "version": "1.0.0"
}
```

### Step 6: Update Node.js Backend

Add to your backend environment variables on Render:

```
MEMORY_SERVICE_URL = https://your-memory-service.onrender.com
```

### Step 7: Test the Integration

Send 25+ messages through your chatbot and watch for:
- Memory compression happening
- Relevant memories being retrieved
- Context maintained across conversations

---

## Quick Deploy Commands (Alternative)

If you prefer CLI:

```bash
# Install Render CLI
npm install -g @renderinc/cli

# Login
render login

# Deploy
render deploy
```

---

## 🎯 Current Status

- ✅ Code in GitHub
- ✅ Python 3.14 compatible
- ⏳ Ready to deploy to Render
- ⏳ Will work perfectly on production servers (no path issues)

---

## Next: Follow Visual Guide

I'll walk you through the Render deployment now! 🚀
