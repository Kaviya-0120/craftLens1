# 🎯 CraftLens - Complete Deployment Steps

## 📝 What We've Done

✅ **Backend Optimized for Free Tier:**
- Replaced torch/whisper with Groq API (~1.5GB → 0MB)
- Replaced rembg/opencv with API calls (~500MB → 0MB)
- Replaced sentence-transformers (~500MB → 0MB)
- **New memory footprint: ~200-300MB** (fits Render's 512MB!)

✅ **Files Updated:**
- `requirements.txt` - Lightweight dependencies
- `asr_service.py` - Groq Whisper API support
- `image_service.py` - remove.bg API + Pillow
- `config.py` - New settings for free tier

✅ **Documentation Created:**
- README.md - Project overview
- RENDER_DEPLOY.md - Deployment guide
- LOCAL_RUN.md - Local development
- GITHUB_PUSH.md - Git workflow
- DEMO_PRESENTATION.md - Presentation script
- QUICK_REFERENCE.md - Quick commands
- push_to_github.bat - Auto-push script

---

## 🚀 YOUR NEXT STEPS

### **STEP 1: PUSH TO GITHUB** (5 minutes)

#### Option A: Automated (Easiest)
```bash
# Double-click this file:
push_to_github.bat
```

#### Option B: Manual Commands
```bash
# Open Command Prompt in this folder
# Right-click folder → "Open in Terminal"

# Check git status
git status

# Add all files
git add .

# Commit
git commit -m "Optimize CraftLens for free tier deployment"

# Check/add remote
git remote -v
# If empty or wrong, run:
git remote add origin https://github.com/Kaviya-0120/craftLens1.git

# Push
git push -u origin main
```

**If push fails with "main doesn't exist":**
```bash
git branch -M main
git push -u origin main
```

**If push fails with authentication:**
- You need a **Personal Access Token** (not your password)
- Get it here: https://github.com/settings/tokens
- Click "Generate new token (classic)"
- Select "repo" scope
- Copy the token
- Use it as password when git asks

✅ **Verify:** Go to https://github.com/Kaviya-0120/craftLens1 and see all files

---

### **STEP 2: DEPLOY BACKEND ON RENDER** (10 minutes)

#### 2.1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub
3. Verify email

#### 2.2: Create New Web Service
1. Click **"New +"** button (top right)
2. Select **"Web Service"**
3. Connect your GitHub repo: **Kaviya-0120/craftLens1**
4. Click **"Connect"**

#### 2.3: Configure Service
Fill in these **EXACT** values:

| Field | Value |
|-------|-------|
| **Name** | `craftlens-backend` |
| **Region** | Singapore (or closest to you) |
| **Branch** | `main` |
| **Root Directory** | `craftlens-backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | **Free** |

#### 2.4: Add Environment Variables
Click **"Advanced"** → **"Add Environment Variable"**

**Copy these EXACTLY** (replace API keys with your actual keys):

```bash
ENVIRONMENT=production
LOG_LEVEL=INFO
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_actual_groq_key_here
GROQ_MODEL=llama-3.1-70b-versatile
GEMINI_API_KEY=AIzaSy_your_actual_gemini_key_here
GEMINI_MODEL=gemini-1.5-flash
ASR_PROVIDER=groq
REMOVEBG_API_KEY=
MAX_UPLOAD_BYTES=10485760
STATIC_DIR=/tmp/static
DATABASE_URL=sqlite+aiosqlite:////tmp/craftlens.db
PRICING_ENABLED=false
ALLOWED_ORIGINS=http://localhost:5173
```

**IMPORTANT:** 
- Change `ASR_PROVIDER` to `groq` (NOT `whisper`)
- Add your actual API keys (no quotes needed)
- Leave `REMOVEBG_API_KEY` empty for now (optional)

#### 2.5: Deploy
1. Click **"Create Web Service"**
2. Wait 5-10 minutes for build
3. Watch logs for errors
4. When complete, you'll see: **"Your service is live at..."**

#### 2.6: Test Backend
```bash
# Copy your Render URL (e.g., https://craftlens-backend.onrender.com)
# Open in browser:
https://your-backend-url.onrender.com/docs

# Should show FastAPI documentation
```

✅ **Success:** You see the API docs page!

---

### **STEP 3: DEPLOY FRONTEND ON VERCEL** (5 minutes)

#### 3.1: Update Frontend Config
**File:** `craftlens-frontend/.env.production` (create if doesn't exist)

```bash
VITE_API_BASE_URL=https://your-actual-backend-url.onrender.com
```

Replace with your **actual Render URL** from Step 2!

#### 3.2: Deploy to Vercel

**Option A: Using Vercel CLI (Recommended)**
```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend
cd craftlens-frontend

# Login (first time only)
vercel login

# Deploy
vercel --prod
```

**Option B: Using Vercel Dashboard**
1. Go to https://vercel.com
2. Sign up with GitHub
3. Click **"Add New Project"**
4. Import `Kaviya-0120/craftLens1`
5. Configure:
   - **Root Directory:** `craftlens-frontend`
   - **Framework:** Vite
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
6. Environment Variables:
   ```
   VITE_API_BASE_URL=https://your-backend-url.onrender.com
   ```
7. Click **"Deploy"**

#### 3.3: Update Backend CORS
Go back to Render:
1. Dashboard → `craftlens-backend` → Environment
2. Edit `ALLOWED_ORIGINS`:
   ```
   ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:5173
   ```
3. Save (service will restart automatically)

✅ **Success:** Your frontend is live!

---

### **STEP 4: TEST EVERYTHING** (5 minutes)

#### 4.1: Test Backend Health
```bash
curl https://your-backend.onrender.com/health
# Should return: {"status":"healthy"}
```

#### 4.2: Test Frontend
1. Open `https://your-frontend.vercel.app`
2. Try these features:
   - ✅ Voice recording
   - ✅ Image upload
   - ✅ Listing generation
   - ✅ Marketplace view

#### 4.3: Test on Mobile
1. Open your phone's browser
2. Visit your Vercel URL
3. Test camera capture
4. Test voice recording
5. Check responsive layout

✅ **All working?** You're LIVE! 🎉

---

### **STEP 5: PREPARE FOR DEMO** (Optional)

#### 5.1: Read Demo Guide
Open `DEMO_PRESENTATION.md` - Contains:
- 10-15 minute presentation script
- What to say at each step
- Q&A responses
- Mobile demo tips

#### 5.2: Practice
1. Record yourself doing the demo
2. Time it (should be 10-15 min)
3. Prepare backup screenshots
4. Test on different devices

#### 5.3: Share Links
When presenting, share:
- **Live App:** https://your-frontend.vercel.app
- **GitHub:** https://github.com/Kaviya-0120/craftLens1
- **Backend API:** https://your-backend.onrender.com/docs

---

## 🐛 Troubleshooting

### Backend Build Fails
**Check Render Logs:**
- Dashboard → craftlens-backend → Logs tab
- Look for error messages

**Common issues:**
- ❌ Missing dependencies → Check requirements.txt
- ❌ Python version → Should auto-detect 3.12
- ❌ Build timeout → Retry deployment

### Backend Starts But Crashes
**Check these:**
1. Environment variables set correctly?
2. `ASR_PROVIDER=groq` (not whisper)?
3. API keys valid?
4. Check logs for errors

### Frontend Build Fails
**Common issues:**
- ❌ Node modules → Run `npm install`
- ❌ Environment variables → Check .env.production
- ❌ API URL format → Must be full URL with https://

### CORS Errors
**Symptoms:** Frontend can't reach backend
**Fix:**
1. Check `ALLOWED_ORIGINS` in Render
2. Must include your Vercel URL
3. No trailing slash: ✅ `https://app.vercel.app` ❌ `https://app.vercel.app/`
4. Restart Render service after changing

### Voice Recording Not Working
**Check:**
1. Browser has microphone permission
2. Using HTTPS (not HTTP)
3. `ASR_PROVIDER=groq` in Render env vars
4. Groq API key is valid
5. Check browser console for errors

### Image Upload Fails
**Check:**
1. File size < 10MB
2. Supported formats: jpg, jpeg, png, webp
3. `REMOVEBG_API_KEY` can be empty (will skip bg removal)
4. Check backend logs

### Render Service Sleeping
**Free tier spins down after 15 min inactivity**

**Solution:**
- Use UptimeRobot (free) to ping every 14 min
- Ping URL: `https://your-backend.onrender.com/health`
- Or: Upgrade to paid plan ($7/month)

---

## 💰 Cost Summary

| Service | Free Tier Limits | Monthly Cost |
|---------|------------------|--------------|
| **Render** | 512MB RAM, 750 hours | $0 |
| **Vercel** | 100GB bandwidth | $0 |
| **Groq** | Rate limited | $0 |
| **Gemini** | 60 req/min | $0 |
| **remove.bg** | 50 images | $0 |
| **TOTAL** | | **$0** ✅ |

---

## ✅ Final Checklist

Before presenting:
- [ ] GitHub repo is public and accessible
- [ ] Backend deployed and health check works
- [ ] Frontend deployed and loads correctly
- [ ] Voice recording tested (with sample)
- [ ] Image upload tested (with camera)
- [ ] Listing generation works
- [ ] Marketplace displays products
- [ ] Mobile version tested
- [ ] Demo script reviewed
- [ ] Backup screenshots prepared

---

## 🎯 Quick Commands Reference

### Push Code
```bash
git add .
git commit -m "Your message"
git push origin main
```

### Test Backend Locally
```bash
cd craftlens-backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

### Test Frontend Locally
```bash
cd craftlens-frontend
npm run dev
```

### Deploy Frontend
```bash
cd craftlens-frontend
vercel --prod
```

### Check Backend Health
```bash
curl https://your-backend.onrender.com/health
```

---

## 📞 Get Help

### Check Logs
- **Render:** Dashboard → Logs tab
- **Vercel:** Dashboard → Deployments → View logs
- **Browser:** F12 → Console tab

### API Status
- **Groq:** https://console.groq.com
- **Gemini:** https://aistudio.google.com

### Documentation
- [Render Docs](https://render.com/docs)
- [Vercel Docs](https://vercel.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com)

---

## 🎉 YOU'RE DONE!

Your CraftLens platform is now:
- ✅ Optimized for free tier (512MB RAM)
- ✅ Pushed to GitHub
- ✅ Deployed on Render (backend)
- ✅ Deployed on Vercel (frontend)
- ✅ Mobile-optimized
- ✅ Demo-ready

**Share your creation:**
- Frontend: https://your-app.vercel.app
- Backend: https://your-backend.onrender.com
- GitHub: https://github.com/Kaviya-0120/craftLens1

Now go empower those artisans! 🇮🇳✨🚀

---

**Questions?** Review:
- [Quick Reference](QUICK_REFERENCE.md)
- [Demo Guide](DEMO_PRESENTATION.md)
- [Deployment Details](RENDER_DEPLOY.md)

**Good luck!** 🎤🎉
