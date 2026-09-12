# 🎨 Frontend Deployment Guide - Connect to Backend

## 📋 What You'll Need

After deploying backend on Render, you should have:
- ✅ Backend URL (e.g., `https://craftlens-backend-xxxx.onrender.com`)
- ✅ Backend is running (test at `/health` endpoint)
- ✅ Node.js and npm installed on your computer

---

## 🔍 STEP 1: Get Your Backend URL

### From Render Dashboard:
1. Go to https://dashboard.render.com
2. Click on `craftlens-backend` service
3. Look for the URL at the top right (looks like: `https://craftlens-backend-xxxx.onrender.com`)
4. **Copy this FULL URL** - you'll need it!

### Test Backend is Working:
Open in browser:
```
https://your-actual-backend-url.onrender.com/health
```

Should see:
```json
{"status":"healthy"}
```

Also test API docs:
```
https://your-actual-backend-url.onrender.com/docs
```

Should see FastAPI documentation page.

✅ **Both working?** Backend is ready!

---

## 🔧 STEP 2: Configure Frontend Environment

Your frontend uses `VITE_API_BASE_URL` to know where the backend is.

### Option A: Create .env File (For Local Testing)

```bash
# Navigate to frontend directory
cd c:\Users\kaviy\OneDrive\Desktop\Craftlens-main\Craftlens-main\craftlens-frontend

# Create .env file
notepad .env
```

**Add this line** (replace with YOUR Render URL):
```bash
VITE_API_BASE_URL=https://craftlens-backend-xxxx.onrender.com
```

**IMPORTANT:** 
- Replace `craftlens-backend-xxxx.onrender.com` with YOUR actual Render URL
- No trailing slash at the end
- No quotes around the URL

**Example:**
```bash
VITE_API_BASE_URL=https://craftlens-backend-ab12.onrender.com
```

### Option B: Create .env.production (For Vercel Deploy)

```bash
# Create production environment file
notepad .env.production
```

**Add this line** (replace with YOUR Render URL):
```bash
VITE_API_BASE_URL=https://craftlens-backend-xxxx.onrender.com
```

---

## 🧪 STEP 3: Test Frontend Locally First

Before deploying, let's test that frontend connects to your backend:

```bash
# Make sure you're in frontend directory
cd c:\Users\kaviy\OneDrive\Desktop\Craftlens-main\Craftlens-main\craftlens-frontend

# Install dependencies (if not done)
npm install

# Start development server
npm run dev
```

You should see:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: http://192.168.x.x:5173/
```

### Test the Connection:

1. **Open browser:** http://localhost:5173
2. **Try voice recording:**
   - Click "Voice" tab
   - Record something
   - Should transcribe (calls backend)
3. **Try image upload:**
   - Click "Image" tab  
   - Upload an image
   - Should process (calls backend)

**If you see errors:**
- Check browser console (F12 → Console)
- Look for CORS errors
- Verify `VITE_API_BASE_URL` is correct
- Check backend is still running

---

## 🚫 STEP 4: Update Backend CORS Settings

Your backend needs to allow requests from your frontend domain.

### Go to Render Dashboard:
1. Click on `craftlens-backend` service
2. Go to **Environment** tab
3. Find `ALLOWED_ORIGINS` variable
4. Click **Edit**

### Update ALLOWED_ORIGINS:

**For local testing:**
```
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

**For production (after Vercel deploy):**
```
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:5173
```

**For both:**
```
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:5173,http://localhost:3000
```

**IMPORTANT:**
- No trailing slashes
- Comma-separated (no spaces)
- Include both production and local URLs

### Save and Wait:
- Click **Save Changes**
- Render will restart backend (takes 1-2 minutes)
- Wait for "Live" status

---

## 🚀 STEP 5: Deploy Frontend to Vercel

Now let's deploy the frontend to Vercel!

### Method A: Using Vercel CLI (Recommended)

#### 1. Install Vercel CLI:
```bash
npm install -g vercel
```

#### 2. Login to Vercel:
```bash
vercel login
```

Follow prompts to login (usually opens browser).

#### 3. Navigate to Frontend:
```bash
cd c:\Users\kaviy\OneDrive\Desktop\Craftlens-main\Craftlens-main\craftlens-frontend
```

#### 4. Deploy:
```bash
vercel
```

**First deployment prompts:**
- **Set up and deploy?** → `Y` (Yes)
- **Which scope?** → Select your account
- **Link to existing project?** → `N` (No)
- **What's your project's name?** → `craftlens` (or any name)
- **In which directory is your code located?** → `./` (press Enter)
- **Want to modify settings?** → `N` (No)

Wait for deployment... (takes 2-3 minutes)

You'll see:
```
✅  Production: https://craftlens-xxxxx.vercel.app [copied to clipboard]
```

#### 5. Add Environment Variable:
```bash
vercel env add VITE_API_BASE_URL
```

When prompted:
- **What's the value?** → Paste your Render backend URL
- **Which environments?** → Select `Production` (space to select, Enter to confirm)

#### 6. Redeploy with Environment Variable:
```bash
vercel --prod
```

This redeploys with the environment variable.

---

### Method B: Using Vercel Dashboard

#### 1. Go to Vercel:
https://vercel.com/login

Login with GitHub or email.

#### 2. Import Project:
- Click **"Add New..."** → **"Project"**
- Click **"Import Git Repository"**
- Find and select: `Kaviya-0120/craftLens1`
- Click **"Import"**

#### 3. Configure Project:

| Setting | Value |
|---------|-------|
| **Project Name** | `craftlens-frontend` |
| **Framework Preset** | Vite |
| **Root Directory** | `craftlens-frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |
| **Install Command** | `npm install` |

#### 4. Add Environment Variable:

Click **"Environment Variables"** (expand section):

**Add variable:**
- **Name:** `VITE_API_BASE_URL`
- **Value:** `https://your-actual-backend-url.onrender.com` (YOUR Render URL!)
- **Environment:** Select `Production`, `Preview`, and `Development`

#### 5. Deploy:
- Click **"Deploy"**
- Wait 3-5 minutes
- You'll get: `https://craftlens-frontend-xxxxx.vercel.app`

---

## ✅ STEP 6: Update Backend CORS (Again!)

Now that frontend is deployed, update backend to allow the Vercel URL:

### Go to Render:
1. Dashboard → `craftlens-backend` → **Environment**
2. Edit `ALLOWED_ORIGINS`:

```
ALLOWED_ORIGINS=https://craftlens-frontend-xxxxx.vercel.app,http://localhost:5173
```

**Replace** `craftlens-frontend-xxxxx.vercel.app` with YOUR actual Vercel URL!

3. **Save Changes**
4. Wait for backend to restart (1-2 min)

---

## 🧪 STEP 7: Test Production Deployment

### Test Your Live App:

1. **Open your Vercel URL** in browser
2. **Try voice recording** - should call backend and transcribe
3. **Try image upload** - should process
4. **Try generating listing** - should work
5. **Open browser console** (F12) - should see no errors

### Test on Mobile:

1. Open phone browser
2. Visit your Vercel URL: `https://your-app.vercel.app`
3. Test camera capture
4. Test voice recording
5. Check responsiveness

### Common Issues:

**CORS Error:**
```
Access to fetch at 'https://backend...' from origin 'https://frontend...' 
has been blocked by CORS policy
```
**Fix:** Update `ALLOWED_ORIGINS` in Render to include your Vercel URL

**Network Error:**
```
POST https://undefined/voice/transcribe 404 (Not Found)
```
**Fix:** `VITE_API_BASE_URL` environment variable not set in Vercel

**Connection Refused:**
```
Failed to fetch
```
**Fix:** Backend is sleeping (free tier) - visit backend URL first to wake it

---

## 🔄 STEP 8: Make Changes Later

### Update Frontend Code:

```bash
# Make changes to your code
# Then push to GitHub:
cd c:\Users\kaviy\OneDrive\Desktop\Craftlens-main\Craftlens-main
git add .
git commit -m "Update frontend"
git push origin main

# Vercel auto-deploys from GitHub!
# Or manually redeploy:
cd craftlens-frontend
vercel --prod
```

### Update Environment Variable:

**Vercel CLI:**
```bash
vercel env rm VITE_API_BASE_URL production
vercel env add VITE_API_BASE_URL production
# Enter new value
vercel --prod
```

**Vercel Dashboard:**
1. Project Settings → Environment Variables
2. Edit `VITE_API_BASE_URL`
3. Save
4. Redeploy from Deployments tab

---

## 📋 Quick Reference

### Your URLs:
```
Backend:  https://craftlens-backend-xxxx.onrender.com
Frontend: https://craftlens-frontend-xxxx.vercel.app
API Docs: https://craftlens-backend-xxxx.onrender.com/docs
```

### Environment Variables:

**Backend (Render):**
```bash
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:5173
```

**Frontend (Vercel):**
```bash
VITE_API_BASE_URL=https://your-backend.onrender.com
```

### Test Commands:

```bash
# Test backend
curl https://your-backend.onrender.com/health

# Run frontend locally
cd craftlens-frontend
npm run dev

# Deploy frontend
vercel --prod
```

---

## 🐛 Troubleshooting

### Frontend can't reach backend

**Check:**
1. ✅ Backend is running (visit `/health` endpoint)
2. ✅ `VITE_API_BASE_URL` is set in Vercel
3. ✅ `ALLOWED_ORIGINS` includes Vercel URL in Render
4. ✅ No typos in URLs (no trailing slashes!)

### Voice/Image upload fails

**Check:**
1. ✅ API endpoints work in backend `/docs`
2. ✅ Groq API key is set in Render
3. ✅ Browser console for specific errors
4. ✅ Network tab in DevTools (F12)

### Vercel build fails

**Check:**
1. ✅ `package.json` has correct scripts
2. ✅ Root directory is `craftlens-frontend`
3. ✅ Build command is `npm run build`
4. ✅ Check Vercel build logs for errors

### Backend sleeping (free tier)

**Symptoms:** First request takes 30-60 seconds

**Solutions:**
- Use UptimeRobot to ping every 14 minutes
- Upgrade to paid plan ($7/month)
- Accept cold starts on free tier

---

## ✅ Success Checklist

- [ ] Backend deployed and `/health` works
- [ ] Backend `/docs` page loads
- [ ] Frontend `.env.production` has correct backend URL
- [ ] Frontend deployed to Vercel
- [ ] Vercel environment variable `VITE_API_BASE_URL` is set
- [ ] Backend `ALLOWED_ORIGINS` includes Vercel URL
- [ ] Frontend loads without errors
- [ ] Voice recording works
- [ ] Image upload works
- [ ] Listing generation works
- [ ] Mobile version works
- [ ] No CORS errors in console

---

## 🎉 You're Live!

Your complete CraftLens platform is now deployed:

- ✅ **Backend:** Render (API + AI services)
- ✅ **Frontend:** Vercel (React app)
- ✅ **Connected:** Frontend ↔️ Backend
- ✅ **Mobile:** Fully responsive
- ✅ **Cost:** $0 (free tiers!)

**Share your app:**
- 🌐 https://your-app.vercel.app
- 📱 Works on phones
- 🎤 Voice recording
- 📸 Image upload
- 🤖 AI listing generation

---

**Next:** Read [DEMO_PRESENTATION.md](DEMO_PRESENTATION.md) to prepare your impressive demo! 🎤✨

<function_calls>
<invoke name="file_search">
<parameter name="query">API_BASE_URL