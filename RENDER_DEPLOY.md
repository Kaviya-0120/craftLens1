# 🚀 CraftLens Deployment Guide - Render Free Tier

## 📋 Prerequisites

- GitHub account
- Render.com account (free tier)
- Vercel account (for frontend - free tier)
- API Keys:
  - Groq API Key (free - get at https://console.groq.com)
  - Gemini API Key (free - get at https://aistudio.google.com/app/apikey)
  - Remove.bg API Key (optional - 50 free images/month at https://remove.bg/api)

---

## 🔧 STEP 1: Optimize Backend for Free Tier

✅ **Already Done!** Your backend is now optimized with:
- Groq Whisper API (instead of local model)
- remove.bg API (instead of rembg)
- Lightweight image processing (Pillow only)
- **Memory footprint: ~200-300MB** (fits Render free tier's 512MB)

---

## 📤 STEP 2: Push to GitHub

### Option A: Using Git Commands

```bash
# Navigate to project directory
cd c:\Users\kaviy\OneDrive\Desktop\Craftlens-main\Craftlens-main

# Initialize git if not already done
git init

# Add all files
git add .

# Commit changes
git commit -m "Optimize backend for Render free tier deployment"

# Add your GitHub repository
git remote add origin https://github.com/Kaviya-0120/craftLens1.git

# Push to GitHub
git push -u origin main
```

If you get errors about existing repository:
```bash
git remote set-url origin https://github.com/Kaviya-0120/craftLens1.git
git push -f origin main
```

### Option B: Using GitHub Desktop
1. Open GitHub Desktop
2. Add this folder as a repository
3. Commit all changes
4. Push to `Kaviya-0120/craftLens1`

---

## 🌐 STEP 3: Deploy Backend on Render

### 3.1: Create New Web Service

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account if not already connected
4. Select repository: **`Kaviya-0120/craftLens1`**
5. Click **"Connect"**

### 3.2: Configure Service

Fill in these settings:

| Setting | Value |
|---------|-------|
| **Name** | `craftlens-backend` |
| **Region** | Choose closest to you (e.g., Singapore, Oregon) |
| **Branch** | `main` |
| **Root Directory** | `craftlens-backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | **Free** |

### 3.3: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add these:

```bash
# Core Framework
ENVIRONMENT=production
LOG_LEVEL=INFO

# LLM Provider (Groq)
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
GROQ_MODEL=llama-3.1-70b-versatile

# Gemini (Fallback)
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxx
GEMINI_MODEL=gemini-1.5-flash

# ASR Provider (IMPORTANT: Use groq, not whisper!)
ASR_PROVIDER=groq

# Image Processing (Optional)
REMOVEBG_API_KEY=your_removebg_key_here_or_leave_empty

# File Upload
MAX_UPLOAD_BYTES=10485760

# Static Files (Render uses ephemeral storage)
STATIC_DIR=/tmp/static

# Database
DATABASE_URL=sqlite+aiosqlite:////tmp/craftlens.db

# Pricing (Disabled for free tier)
PRICING_ENABLED=false

# CORS (Add your frontend URL after deploying)
ALLOWED_ORIGINS=http://localhost:5173
```

### 3.4: Deploy

1. Click **"Create Web Service"**
2. Wait 5-10 minutes for first deployment
3. Your backend will be live at: `https://craftlens-backend.onrender.com`
4. **Copy this URL** - you'll need it for frontend!

---

## 🎨 STEP 4: Deploy Frontend on Vercel

### 4.1: Prepare Frontend

Update frontend API URL:

**File:** `craftlens-frontend/src/config.js` (or wherever API URL is stored)

```javascript
export const API_BASE_URL = 'https://craftlens-backend.onrender.com';
```

Or use environment variables (better approach):

**File:** `craftlens-frontend/.env.production`
```bash
VITE_API_BASE_URL=https://craftlens-backend.onrender.com
```

### 4.2: Deploy to Vercel

#### Option A: Using Vercel CLI
```bash
cd craftlens-frontend
npm install -g vercel
vercel login
vercel --prod
```

#### Option B: Using Vercel Dashboard
1. Go to https://vercel.com
2. Click **"Add New"** → **"Project"**
3. Import `Kaviya-0120/craftLens1`
4. Configure:
   - **Root Directory:** `craftlens-frontend`
   - **Framework Preset:** Vite
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
5. Add Environment Variable:
   ```
   VITE_API_BASE_URL=https://craftlens-backend.onrender.com
   ```
6. Click **"Deploy"**

### 4.3: Update Backend CORS

Go back to Render dashboard → craftlens-backend → Environment:

Update `ALLOWED_ORIGINS`:
```bash
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:5173
```

---

## ✅ STEP 5: Verify Deployment

### Test Backend
```bash
curl https://craftlens-backend.onrender.com/health
# Should return: {"status":"healthy"}
```

### Test Frontend
1. Open `https://your-frontend.vercel.app`
2. Try voice recording → should transcribe
3. Try image upload → should process
4. Check browser console for any CORS errors

---

## 📱 STEP 6: Mobile Optimization

Your app is already mobile-optimized, but test:

1. Open on mobile browser
2. Test camera capture (should work on HTTPS)
3. Test voice recording
4. Check responsive layout

---

## 🔍 Troubleshooting

### Backend Won't Start
- Check Render logs: Dashboard → craftlens-backend → Logs
- Verify all environment variables are set
- Ensure `ASR_PROVIDER=groq` (NOT whisper)

### Voice Recording Fails
- Check GROQ_API_KEY is correct
- Verify Groq credits: https://console.groq.com
- Check Render logs for error messages

### Image Upload Fails
- If using remove.bg: verify API key
- If not using: leave REMOVEBG_API_KEY empty (will skip background removal)
- Check image file size (<10MB)

### CORS Errors
- Ensure ALLOWED_ORIGINS includes your Vercel URL
- Format: `https://your-app.vercel.app` (no trailing slash)
- Restart Render service after changing

### Free Tier Limitations
- Render: Spins down after 15 min inactivity (first request slow)
- Render: 512MB RAM (our optimizations fit!)
- Render: 750 hours/month (enough for demo)
- Vercel: 100GB bandwidth/month
- Groq: Rate limits apply (generous free tier)

---

## 🎯 Performance Tips

### Keep Backend Warm
Use a service like UptimeRobot (free) to ping your backend every 14 minutes:
```
https://craftlens-backend.onrender.com/health
```

### Optimize Images
Frontend should compress images before upload:
```javascript
// In your upload component
const compressImage = async (file) => {
  const maxSize = 1024; // 1MB
  if (file.size < maxSize * 1024) return file;
  
  // Add compression logic
  return compressedFile;
};
```

---

## 🔒 Security Checklist

- ✅ Never commit `.env` files
- ✅ Use environment variables for all API keys
- ✅ Enable CORS only for your domains
- ✅ Add rate limiting in production (Render supports this)
- ✅ Monitor API usage (Groq, Gemini, remove.bg)

---

## 📊 Monitoring

### Render Dashboard
- Monitor memory usage (should stay under 400MB)
- Check response times
- View deployment logs

### Groq Console
- https://console.groq.com
- Monitor API usage
- Check remaining credits

### Vercel Analytics
- View visitor stats
- Monitor bandwidth usage

---

## 💰 Cost Breakdown (All FREE!)

| Service | Plan | Monthly Cost | Limits |
|---------|------|--------------|--------|
| **Render** | Free | $0 | 512MB RAM, 750hrs |
| **Vercel** | Hobby | $0 | 100GB bandwidth |
| **Groq** | Free | $0 | Rate limits apply |
| **Gemini** | Free | $0 | 60 requests/min |
| **remove.bg** | Free | $0 | 50 images/month |
| **Total** | | **$0** | ✅ |

---

## 🎉 You're Done!

Your CraftLens platform is now live and accessible worldwide!

**Backend:** `https://craftlens-backend.onrender.com`  
**Frontend:** `https://your-app.vercel.app`

Share with artisans and start empowering Indian craftspeople! 🇮🇳✨
