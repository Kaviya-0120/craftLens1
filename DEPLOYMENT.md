# CraftLens Deployment Guide (Mobile-Optimized)

This guide will help you deploy CraftLens to production with full mobile support.

## 📱 Mobile Features
- ✅ Camera capture for product photos
- ✅ Touch-optimized UI
- ✅ Responsive design for all screen sizes
- ✅ PWA support (installable on mobile)
- ✅ Optimized for Android & iOS

---

## 🚀 Quick Deployment (Recommended)

### **Option 1: Deploy Both (Frontend + Backend)**

#### **1. Deploy Backend on Render**

1. Go to [Render.com](https://render.com) and sign up/login
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `Kaviya-0120/craftLens1`
4. Configure:
   - **Name**: `craftlens-backend`
   - **Root Directory**: `craftlens-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
5. Add Environment Variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `GEMINI_API_KEY`: Your Google Gemini API key (if using)
6. Click **"Create Web Service"**
7. Wait for deployment (5-10 minutes)
8. Copy your backend URL: `https://craftlens-backend-xxxx.onrender.com`

#### **2. Deploy Frontend on Vercel**

1. Go to [Vercel.com](https://vercel.com) and sign up/login
2. Click **"New Project"**
3. Import repository: `Kaviya-0120/craftLens1`
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `craftlens-frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add Environment Variable:
   - **Name**: `VITE_API_BASE_URL`
   - **Value**: `https://craftlens-backend-xxxx.onrender.com` (your backend URL)
6. Click **"Deploy"**
7. Wait for deployment (2-3 minutes)
8. Your app is live! 🎉

---

## 📱 Testing on Mobile

### **Android:**
1. Open Chrome browser
2. Visit your Vercel URL
3. Test camera capture, voice recording, all features
4. Click menu → "Add to Home Screen" to install as PWA

### **iOS:**
1. Open Safari browser
2. Visit your Vercel URL
3. Tap share button → "Add to Home Screen"
4. App will work like a native app

---

## 🔧 Alternative Deployment Options

### **Option 2: Netlify (Frontend Alternative)**

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd craftlens-frontend
netlify deploy --prod
```

### **Option 3: Railway (Backend Alternative)**

1. Go to [Railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Select `craftlens-backend` folder
4. Add environment variables
5. Deploy automatically

### **Option 4: Heroku (Both)**

```bash
# Install Heroku CLI
# Backend
cd craftlens-backend
heroku create craftlens-backend
git push heroku main

# Frontend
cd craftlens-frontend
heroku create craftlens-frontend
heroku buildpacks:set heroku/nodejs
git push heroku main
```

---

## 🌐 Custom Domain (Optional)

### **For Vercel:**
1. Go to Project Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

### **For Render:**
1. Go to Settings → Custom Domain
2. Add your domain
3. Update DNS records

---

## 🔒 Security Checklist

- ✅ Add HTTPS (automatic on Vercel/Render)
- ✅ Set environment variables (never commit API keys)
- ✅ Enable CORS on backend
- ✅ Add rate limiting (optional)
- ✅ Enable authentication (optional)

---

## 📊 Performance Optimization

### **Frontend (Already Done):**
- ✅ Lazy loading images
- ✅ Code splitting
- ✅ Minified assets
- ✅ Mobile-first design

### **Backend:**
- ✅ Caching responses
- ✅ Compression enabled
- ✅ Async operations

---

## 🐛 Troubleshooting

### **Camera not working on mobile:**
- Ensure HTTPS is enabled (required for camera API)
- Check browser permissions
- Test on Chrome/Safari (most compatible)

### **API calls failing:**
- Verify `VITE_API_BASE_URL` is set correctly
- Check CORS settings on backend
- Ensure backend is running

### **Slow performance:**
- Enable caching
- Use CDN for images
- Optimize image sizes

---

## 📈 Monitoring

### **Vercel Analytics:**
- Enable in Project Settings
- Track page views, performance

### **Render Metrics:**
- View in dashboard
- Monitor CPU, memory usage

---

## 🔄 Continuous Deployment

Both Vercel and Render support automatic deployments:
1. Push to GitHub `main` branch
2. Automatic deployment triggers
3. Live in 2-5 minutes

```bash
git add .
git commit -m "Update feature"
git push origin main
```

---

## 💰 Cost Estimate

### **Free Tier (Perfect for MVP):**
- **Vercel**: 100GB bandwidth/month (FREE)
- **Render**: 750 hours/month (FREE)
- **Total**: $0/month

### **Paid Tier (For Production):**
- **Vercel Pro**: $20/month
- **Render Starter**: $7/month
- **Total**: ~$27/month

---

## 📞 Support

- **Vercel Docs**: https://vercel.com/docs
- **Render Docs**: https://render.com/docs
- **GitHub Issues**: https://github.com/Kaviya-0120/craftLens1/issues

---

## ✅ Post-Deployment Checklist

- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible
- [ ] Environment variables configured
- [ ] Test on Android phone
- [ ] Test on iOS phone
- [ ] Camera capture working
- [ ] Voice recording working
- [ ] Image upload working
- [ ] Marketplace loading
- [ ] Login flows working
- [ ] PWA installable
- [ ] Share link with users

---

🎉 **Your CraftLens app is now live and mobile-ready!**
