# 🏃 CraftLens Local Development Guide

## 📋 Prerequisites

1. **Python 3.10+** installed
2. **Node.js 18+** and npm installed
3. **Git** installed
4. **API Keys** (free):
   - Groq API Key → https://console.groq.com
   - Gemini API Key → https://aistudio.google.com/app/apikey

---

## 🚀 Quick Start (Step by Step)

### STEP 1: Clone Repository

```bash
# Open Command Prompt (Windows) or Terminal (Mac/Linux)
cd C:\Users\kaviy\OneDrive\Desktop

# If you haven't pushed to GitHub yet, skip this
# git clone https://github.com/Kaviya-0120/craftLens1.git
# cd craftLens1

# If working with existing folder
cd Craftlens-main\Craftlens-main
```

---

### STEP 2: Setup Backend

#### 2.1: Navigate to Backend
```bash
cd craftlens-backend
```

#### 2.2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 2.3: Install Dependencies
```bash
pip install -r requirements.txt
```

This will take 3-5 minutes. You should see packages installing.

#### 2.4: Configure Environment Variables

**Option A: Copy and edit .env file**
```bash
# Windows
copy .env.example .env
notepad .env

# Mac/Linux
cp .env.example .env
nano .env
```

**Option B: Use the existing .env**

Your `.env` file should contain:
```bash
# LLM Configuration
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_actual_key_here
GROQ_MODEL=llama-3.1-70b-versatile

GEMINI_API_KEY=AIzaSy_your_actual_key_here
GEMINI_MODEL=gemini-1.5-flash

# ASR Configuration (IMPORTANT!)
ASR_PROVIDER=groq

# Image Processing (Optional)
REMOVEBG_API_KEY=

# App Settings
APP_ENV=development
STATIC_DIR=./static
MAX_UPLOAD_BYTES=10485760
DATABASE_URL=sqlite+aiosqlite:///./craftlens.db

# Pricing (Disable for now)
PRICING_ENABLED=false
```

#### 2.5: Start Backend Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **Backend is running!** Keep this terminal open.

Test it: Open browser → `http://localhost:8000/docs` (should show API documentation)

---

### STEP 3: Setup Frontend

#### 3.1: Open NEW Terminal/Command Prompt
Don't close the backend terminal! Open a new one.

```bash
cd C:\Users\kaviy\OneDrive\Desktop\Craftlens-main\Craftlens-main\craftlens-frontend
```

#### 3.2: Install Dependencies
```bash
npm install
```

This will take 2-3 minutes.

#### 3.3: Configure API URL

**File:** `craftlens-frontend/.env` (create if doesn't exist)
```bash
VITE_API_BASE_URL=http://localhost:8000
```

Or update the config file directly:

**File:** `craftlens-frontend/src/config.js`
```javascript
export const API_BASE_URL = 'http://localhost:8000';
```

#### 3.4: Start Frontend Server
```bash
npm run dev
```

You should see:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: http://192.168.x.x:5173/
➜  press h to show help
```

✅ **Frontend is running!**

---

### STEP 4: Open Application

1. Open browser → `http://localhost:5173`
2. You should see the CraftLens home page
3. Try the features:
   - ✅ Voice recording
   - ✅ Image upload
   - ✅ Listing generation
   - ✅ Marketplace

---

## 📱 Test on Mobile (Same WiFi)

1. Find your computer's IP address:
   ```bash
   # Windows
   ipconfig
   # Look for "IPv4 Address" (e.g., 192.168.1.5)

   # Mac/Linux
   ifconfig
   # or
   ip addr
   ```

2. On your phone's browser, visit:
   ```
   http://YOUR_IP:5173
   ```
   Example: `http://192.168.1.5:5173`

3. Test camera capture and voice recording!

---

## 🛑 Stop Servers

### Stop Frontend
In the frontend terminal, press: **CTRL + C**

### Stop Backend
In the backend terminal, press: **CTRL + C**

Then deactivate virtual environment:
```bash
deactivate
```

---

## 🔄 Restart Servers (Next Time)

### Backend
```bash
cd C:\Users\kaviy\OneDrive\Desktop\Craftlens-main\Craftlens-main\craftlens-backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

### Frontend (New Terminal)
```bash
cd C:\Users\kaviy\OneDrive\Desktop\Craftlens-main\Craftlens-main\craftlens-frontend
npm run dev
```

---

## 🐛 Troubleshooting

### Backend Errors

#### "ModuleNotFoundError: No module named 'xyz'"
```bash
pip install -r requirements.txt
```

#### "GROQ_API_KEY not set"
- Check `.env` file exists in `craftlens-backend/`
- Verify API key is correct (no quotes, no spaces)
- Restart backend after editing `.env`

#### "Address already in use"
Backend port 8000 is busy:
```bash
# Use different port
uvicorn app.main:app --reload --port 8001

# Update frontend config to http://localhost:8001
```

#### "whisper not found" or "torch not found"
Make sure `ASR_PROVIDER=groq` in `.env` (not `whisper`)

### Frontend Errors

#### "Cannot connect to backend"
- Check backend is running (`http://localhost:8000/docs`)
- Verify `VITE_API_BASE_URL` in frontend `.env`
- Check browser console for CORS errors

#### "npm: command not found"
Install Node.js: https://nodejs.org (LTS version)

#### Port 5173 already in use
```bash
# Vite will auto-increment to 5174
# or specify port:
npm run dev -- --port 3000
```

### Voice Recording Not Working

1. Browser must have microphone permission
2. Use HTTPS or localhost (HTTP won't work for mic)
3. Check Groq API key is valid
4. Check browser console for errors

### Image Upload Not Working

1. Check file size (<10MB)
2. Supported formats: jpg, jpeg, png, webp
3. Check backend logs for errors
4. If using remove.bg: verify API key

---

## 📊 Verify API Keys

### Test Groq API
```bash
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer YOUR_GROQ_KEY"
```

### Test Gemini API
```bash
curl "https://generativelanguage.googleapis.com/v1/models?key=YOUR_GEMINI_KEY"
```

Both should return JSON (not errors).

---

## 🎯 Development Workflow

1. **Start backend first** (port 8000)
2. **Then start frontend** (port 5173)
3. **Make changes** (both auto-reload)
4. **Test features** in browser
5. **Check logs** in both terminals
6. **Stop servers** when done (CTRL+C)

---

## 📝 Project Structure

```
Craftlens-main/
├── craftlens-backend/          ← Python FastAPI
│   ├── app/
│   │   ├── main.py            ← Entry point
│   │   ├── config.py          ← Settings
│   │   ├── routers/           ← API endpoints
│   │   ├── services/          ← Business logic
│   │   └── models/            ← Data schemas
│   ├── requirements.txt       ← Python dependencies
│   └── .env                   ← API keys (NEVER commit!)
│
└── craftlens-frontend/         ← React + Vite
    ├── src/
    │   ├── App.jsx            ← Main component
    │   ├── components/        ← UI components
    │   └── config.js          ← API URL
    ├── package.json           ← Node dependencies
    └── .env                   ← Frontend config
```

---

## 🎓 Next Steps

1. ✅ Run locally (you're here!)
2. 📤 Push to GitHub
3. 🌐 Deploy to Render + Vercel (see RENDER_DEPLOY.md)
4. 📱 Test on mobile
5. 🎉 Share with artisans!

---

## 💡 Tips

- **Keep terminals open** while developing
- **Check logs** if something breaks
- **Use browser DevTools** (F12) to debug frontend
- **Backend logs** show in terminal
- **Hot reload** works for both frontend and backend
- **Test on mobile** before deploying

---

## 🆘 Need Help?

Check logs for errors:
- **Backend:** Terminal where uvicorn is running
- **Frontend:** Browser console (F12 → Console tab)
- **Network:** Browser DevTools → Network tab

Common issues:
1. ❌ Wrong API keys → check `.env`
2. ❌ Backend not running → check port 8000
3. ❌ CORS errors → check `ALLOWED_ORIGINS`
4. ❌ Module errors → run `pip install -r requirements.txt`

---

Happy coding! 🚀✨
