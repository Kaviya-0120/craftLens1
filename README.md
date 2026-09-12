# 🎨 CraftLens - AI-Powered Artisan Marketplace

> Empowering Indian artisans to create professional product listings using voice and images - in any language, with zero cost.

[![Made in India](https://img.shields.io/badge/Made%20in-India-orange?style=flat-square)](https://en.wikipedia.org/wiki/India)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=flat-square&logo=react)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

## 📖 The Problem

India has **200+ million artisans** creating beautiful handcrafted products. But **95% struggle online** because:

- ❌ They don't speak English well
- ❌ They can't afford professional photography
- ❌ E-commerce platforms are too complicated
- ❌ They don't know how to price their work

**Result:** Beautiful crafts remain unseen. Artisans earn ₹5,000-15,000/month while middlemen take 30-50% commission.

---

## ✨ The Solution

**CraftLens** uses AI to transform voice + images into professional marketplace listings:

| Traditional Way | CraftLens Way |
|-----------------|---------------|
| 2-3 hours setup | **5 minutes** |
| Must speak English | **Any Indian language** |
| ₹5,000+ for photography | **₹0** (phone camera) |
| Fill 50+ form fields | **Just speak naturally** |
| Guess pricing | **AI suggests fair price** |
| 30% platform commission | **0% commission** |

---

## 🎥 Demo

**From Voice to Marketplace in 5 Minutes:**

1. 🎤 **Voice Recording** - Describe product in your language
2. 📸 **Image Upload** - Capture with phone camera
3. 🤖 **AI Magic** - Generates professional listing
4. 💰 **Smart Pricing** - AI suggests fair market price
5. 🌐 **Publish** - Goes live on marketplace instantly

[See Full Demo Guide →](DEMO_PRESENTATION.md)

---

## 🏗️ Architecture

### Frontend
- **Framework:** React 18 + Vite
- **Styling:** Tailwind CSS
- **Features:** PWA, Mobile-first, Offline-capable
- **Deploy:** Vercel (free tier)

### Backend
- **Framework:** FastAPI (Python)
- **AI Services:**
  - 🎤 **Voice:** Groq Whisper API (free)
  - 🧠 **LLM:** Groq (Llama 3.1) + Gemini (fallback)
  - 🖼️ **Image:** remove.bg API (optional)
  - 💰 **Pricing:** Gemini embeddings
- **Database:** SQLite (aiosqlite)
- **Deploy:** Render (free tier - optimized!)

**Memory Footprint:** ~200-300MB (fits free tier's 512MB!)

---

## 🚀 Quick Start

### 📋 Prerequisites
- Python 3.10+
- Node.js 18+
- Free API Keys:
  - [Groq API](https://console.groq.com) - for voice & LLM
  - [Gemini API](https://aistudio.google.com/app/apikey) - for LLM
  - [remove.bg](https://remove.bg/api) (optional) - for background removal

### ⚡ Run Locally

**1. Clone & Setup Backend:**
```bash
cd craftlens-backend
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux
pip install -r requirements.txt

# Create .env file with your API keys
cp .env.example .env
notepad .env                   # Add your API keys

# Start server
uvicorn app.main:app --reload
```

**2. Setup Frontend (New Terminal):**
```bash
cd craftlens-frontend
npm install
npm run dev
```

**3. Open Browser:**
- Frontend: http://localhost:5173
- Backend API Docs: http://localhost:8000/docs

[📖 Detailed Local Setup Guide →](LOCAL_RUN.md)

---

## 🌐 Deploy to Production

### Step 1: Push to GitHub
```bash
# Option A: Use automated script (Windows)
push_to_github.bat

# Option B: Manual commands
git add .
git commit -m "Deploy CraftLens"
git push origin main
```

[📖 GitHub Push Guide →](GITHUB_PUSH.md)

### Step 2: Deploy Backend (Render)
1. Create account at [Render.com](https://render.com)
2. New Web Service → Connect GitHub repo
3. Configure (see guide below)
4. Add environment variables
5. Deploy! ✨

[📖 Complete Deployment Guide →](RENDER_DEPLOY.md)

### Step 3: Deploy Frontend (Vercel)
```bash
cd craftlens-frontend
npm install -g vercel
vercel --prod
```

[📖 Quick Reference →](QUICK_REFERENCE.md)

---

## 🎤 Demo & Presentation

Planning to showcase CraftLens? We've got you covered:

**[📖 Complete Demo Script →](DEMO_PRESENTATION.md)**

Includes:
- 10-15 minute presentation flow
- What to say at each step
- How to handle Q&A
- Mobile demo tips
- Impressive statistics to share

**Key Talking Points:**
- 🎯 5-minute listing vs. 2-3 hours
- 🗣️ Any Indian language (not just English)
- 💰 ₹0 cost to artisans (no commission!)
- 📱 Works on ₹5,000 smartphone
- 🇮🇳 200 million artisan market

---

## 🛠️ Tech Stack

### AI & ML
- **Groq Whisper API** - Speech-to-text (multilingual)
- **Groq Llama 3.1** - LLM for listing generation
- **Google Gemini** - Fallback LLM + embeddings
- **remove.bg API** - Background removal (optional)
- **Pillow** - Lightweight image processing

### Backend
- **FastAPI** - High-performance API framework
- **Pydantic** - Data validation
- **SQLAlchemy** - Database ORM
- **aiosqlite** - Async SQLite
- **httpx** - Async HTTP client

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client

### DevOps
- **Render** - Backend hosting (free tier)
- **Vercel** - Frontend hosting (free tier)
- **GitHub Actions** - CI/CD (optional)

---

## 📊 Features

### ✅ Implemented
- [x] Voice recording & transcription (multilingual)
- [x] Image upload with camera capture
- [x] Background removal
- [x] AI listing generation (bilingual)
- [x] Smart pricing suggestions
- [x] Consistency verification
- [x] Customer marketplace
- [x] Dual login (Artisan + Customer)
- [x] Mobile-first responsive design
- [x] PWA support
- [x] Direct artisan contact (WhatsApp/Phone)

### 🔄 In Progress
- [ ] User authentication (JWT)
- [ ] Payment integration
- [ ] Review system
- [ ] Analytics dashboard
- [ ] Multi-product stores

### 🔮 Planned
- [ ] Mobile app (React Native)
- [ ] SMS integration (for feature phones)
- [ ] Regional language UI
- [ ] Bulk upload
- [ ] Export catalogs (PDF/Excel)

---

## 🌍 Impact

### Target Users
- **Primary:** 200 million Indian artisans
- **Secondary:** Rural craftspeople, weavers, potters
- **Geography:** Pan-India (focus: UP, Gujarat, Rajasthan, Tamil Nadu)

### Social Impact
- ♿ Digital inclusion (language barrier removed)
- 💼 Economic empowerment (fair pricing, no middlemen)
- 🎨 Cultural preservation (traditional crafts showcased)
- 🌱 Sustainable livelihoods (direct market access)

### Metrics
- **Time saved:** 95% (5 min vs. 2-3 hours)
- **Cost saved:** 100% (₹0 vs. ₹5,000+)
- **Commission saved:** 30-50% (direct connection)
- **Reach:** Global (vs. local markets)

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

**Areas we need help:**
- [ ] Regional language support (translators needed!)
- [ ] Mobile app development (React Native)
- [ ] UI/UX improvements
- [ ] Documentation
- [ ] Testing

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Indian Artisans** - For inspiring this project
- **Groq** - For free Whisper & Llama API
- **Google** - For Gemini free tier
- **Render & Vercel** - For free hosting
- **Open Source Community** - For amazing tools

---

## 📞 Contact

**Developer:** Kaviya  
**GitHub:** [@Kaviya-0120](https://github.com/Kaviya-0120)  
**Project:** [craftLens1](https://github.com/Kaviya-0120/craftLens1)

---

## 🎯 Project Status

**Current Version:** v1.0.0 (MVP)  
**Status:** ✅ Production Ready  
**Deployment:** ✅ Optimized for Free Tier  
**Mobile:** ✅ Fully Responsive  
**Languages:** 🇮🇳 Hindi, Tamil, Telugu, Bengali + English

---

## 📚 Documentation

- [🏃 Local Development Guide](LOCAL_RUN.md)
- [📤 GitHub Push Guide](GITHUB_PUSH.md)
- [🚀 Deployment Guide](RENDER_DEPLOY.md)
- [🎤 Demo & Presentation](DEMO_PRESENTATION.md)
- [⚡ Quick Reference](QUICK_REFERENCE.md)

---

## 💡 Why CraftLens?

> "Technology should serve everyone, not just English-speakers with degrees. CraftLens proves AI can be **inclusive**, **empowering**, and **profitable**. This is the future of digital India." 🇮🇳

---

<div align="center">

**⭐ Star this repo if you believe in empowering artisans! ⭐**

Made with ❤️ for Indian Artisans

[🚀 Get Started](LOCAL_RUN.md) • [📖 Documentation](RENDER_DEPLOY.md) • [🎤 Demo Guide](DEMO_PRESENTATION.md)

</div>
