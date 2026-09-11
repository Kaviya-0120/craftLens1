# 🚀 Quick Deploy Guide (5 Minutes)

## Step-by-Step Deployment

### 📱 **1. Deploy Backend (3 minutes)**

1. **Go to**: https://render.com
2. Click **"New +"** → **"Web Service"**
3. **Connect GitHub**: Select `Kaviya-0120/craftLens1`
4. **Settings**:
   ```
   Name: craftlens-backend
   Root Directory: craftlens-backend
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
5. **Environment Variables** (click "Advanced" → "Add Environment Variable"):
   ```
   OPENAI_API_KEY = your_openai_key_here
   GEMINI_API_KEY = your_gemini_key_here (optional)
   ```
6. Click **"Create Web Service"**
7. **⚠️ IMPORTANT**: Copy your backend URL (e.g., `https://craftlens-backend-xxxx.onrender.com`)

---

### 🌐 **2. Deploy Frontend (2 minutes)**

1. **Go to**: https://vercel.com
2. Click **"Add New"** → **"Project"**
3. **Import**: `Kaviya-0120/craftLens1`
4. **Configure**:
   ```
   Framework Preset: Vite
   Root Directory: craftlens-frontend
   Build Command: npm run build (auto-detected)
   Output Directory: dist (auto-detected)
   ```
5. **Environment Variables**:
   ```
   Name: VITE_API_BASE_URL
   Value: https://craftlens-backend-xxxx.onrender.com
   (paste your Render backend URL from step 1)
   ```
6. Click **"Deploy"**
7. **Done!** Your URL: `https://craftlens-xxxx.vercel.app`

---

## ✅ Test on Mobile

1. **Open your Vercel URL on phone**
2. **Test features**:
   - ✓ Camera capture (tap "Open Camera")
   - ✓ Voice recording
   - ✓ Image upload
   - ✓ Marketplace browsing
   - ✓ Login (Artisan & Customer)

3. **Install as App** (Optional):
   - **Android**: Chrome menu → "Add to Home Screen"
   - **iOS**: Safari share → "Add to Home Screen"

---

## 🔧 If Something Doesn't Work

### Camera not working?
- ✅ Must use HTTPS (Vercel provides this automatically)
- ✅ Allow camera permissions in browser

### API calls failing?
- ✅ Check `VITE_API_BASE_URL` in Vercel settings
- ✅ Ensure backend is running on Render
- ✅ Backend URL must include `https://`

### Backend sleeping (Free tier)?
- ✅ First request takes 30-60 seconds (free tier spins down)
- ✅ Subsequent requests are fast
- ✅ Upgrade to paid plan ($7/month) for instant responses

---

## 📊 Free Tier Limits

**Render (Backend):**
- ✅ 750 hours/month (enough for 1 app running 24/7)
- ⚠️ Spins down after 15 minutes of inactivity
- ⚠️ First request after spin-down is slow (30-60s)

**Vercel (Frontend):**
- ✅ 100GB bandwidth/month
- ✅ Unlimited requests
- ✅ Always fast (no sleeping)

---

## 🎯 Your URLs

After deployment, save these:

```
Frontend: https://craftlens-xxxx.vercel.app
Backend: https://craftlens-backend-xxxx.onrender.com
GitHub: https://github.com/Kaviya-0120/craftLens1
```

---

## 🔄 Update Your App

```bash
# Make changes to code
git add .
git commit -m "Update message"
git push origin main

# Auto-deploys to Vercel & Render! ✨
```

---

## 💡 Pro Tips

1. **Keep backend warm**: Use a service like [cron-job.org](https://cron-job.org) to ping your backend every 10 minutes
2. **Custom domain**: Add in Vercel/Render settings (free)
3. **Analytics**: Enable Vercel Analytics for free traffic insights
4. **Monitoring**: Both platforms have dashboards to monitor performance

---

## 🎉 You're Live!

Share your app:
- WhatsApp: Send Vercel URL
- QR Code: Generate at [qr-code-generator.com](https://www.qr-code-generator.com)
- Social media: Post your link

**Need help?** Check [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed guide.
