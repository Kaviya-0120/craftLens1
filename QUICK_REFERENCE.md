# 🚀 CraftLens Quick Reference Card

## 📱 Essential URLs

- **GitHub:** https://github.com/Kaviya-0120/craftLens1
- **Backend (Render):** Will be `https://craftlens-backend.onrender.com`
- **Frontend (Vercel):** Will be `https://your-app.vercel.app`

---

## 🔑 Environment Variables (Backend)

```bash
# Copy these to Render Dashboard
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_actual_key_here
GROQ_MODEL=llama-3.1-70b-versatile
GEMINI_API_KEY=AIzaSy_your_actual_key_here
GEMINI_MODEL=gemini-1.5-flash
ASR_PROVIDER=groq
REMOVEBG_API_KEY=
PRICING_ENABLED=false
STATIC_DIR=/tmp/static
DATABASE_URL=sqlite+aiosqlite:////tmp/craftlens.db
MAX_UPLOAD_BYTES=10485760
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:5173
```

---

## ⚡ Quick Commands

### Run Locally

**Backend:**
```bash
cd craftlens-backend
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd craftlens-frontend
npm run dev
```

### Push to GitHub
```bash
git add .
git commit -m "Your message"
git push origin main
```

### Deploy Backend (Render)
1. Dashboard → New Web Service
2. Connect GitHub repo
3. Root dir: `craftlens-backend`
4. Build: `pip install -r requirements.txt`
5. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables
7. Deploy!

### Deploy Frontend (Vercel)
```bash
cd craftlens-frontend
vercel --prod
```

---

## 🐛 Common Issues

| Problem | Solution |
|---------|----------|
| Voice fails | Check `ASR_PROVIDER=groq` in .env |
| Image fails | Set `REMOVEBG_API_KEY` or leave empty |
| CORS error | Update `ALLOWED_ORIGINS` |
| 502 error | Check Render logs |
| Build fails | Verify requirements.txt |

---

## 📊 Demo Flow (5 min version)

1. **Open app** → Show home page (30 sec)
2. **Voice** → Record product description (1 min)
3. **Image** → Upload/capture photo (1 min)
4. **Listing** → Generate with AI (1 min)
5. **Publish** → Show in marketplace (1 min)
6. **Mobile** → Demo responsiveness (30 sec)

---

## 💰 Free Tier Limits

- **Render:** 512MB RAM, 750 hours/month
- **Vercel:** 100GB bandwidth/month
- **Groq:** Rate limits (generous)
- **Gemini:** 60 requests/min
- **remove.bg:** 50 images/month (optional)

---

## 🎯 Key Talking Points

1. **5-minute** listing (vs. hours)
2. **Any language** (not just English)
3. **₹0 cost** to artisans
4. **No commission** (vs. 30% on platforms)
5. **200M** artisan market in India
6. **Mobile-first** (₹5K smartphone works)

---

## 🔗 Important Links

- **Groq Console:** https://console.groq.com
- **Gemini API:** https://aistudio.google.com/app/apikey
- **remove.bg API:** https://remove.bg/api
- **Render Docs:** https://render.com/docs
- **Vercel Docs:** https://vercel.com/docs

---

## 📞 Support

- Check logs: Render dashboard → Logs
- Browser console: F12 → Console tab
- Backend test: `/docs` endpoint
- Health check: `/health` endpoint

---

Keep this handy! 📌✨
