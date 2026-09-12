# 📤 Push CraftLens to GitHub - Step by Step

## 🎯 Goal
Push your optimized CraftLens project to: `https://github.com/Kaviya-0120/craftLens1`

---

## 📋 Prerequisites

1. Git installed on your computer
2. GitHub account (Kaviya-0120)
3. Repository created: `craftLens1`

---

## 🚀 Method 1: Using Git Commands (Recommended)

### Step 1: Open Command Prompt
```bash
# Press Windows key, type "cmd", press Enter
# Or right-click in your project folder → "Open in Terminal"
```

### Step 2: Navigate to Project
```bash
cd C:\Users\kaviy\OneDrive\Desktop\Craftlens-main\Craftlens-main
```

### Step 3: Check Git Status
```bash
git status
```

**If you see "Not a git repository":**
```bash
git init
```

### Step 4: Check Remote Repository
```bash
git remote -v
```

**If nothing appears or wrong URL:**
```bash
# Remove old remote if exists
git remote remove origin

# Add correct remote
git remote add origin https://github.com/Kaviya-0120/craftLens1.git
```

### Step 5: Add All Files
```bash
git add .
```

This stages all your changes.

### Step 6: Commit Changes
```bash
git commit -m "Optimize backend for Render free tier - API-based ML services"
```

### Step 7: Push to GitHub
```bash
# First time push
git push -u origin main
```

**If it asks for credentials:**
- Username: `Kaviya-0120`
- Password: Use **Personal Access Token** (not your GitHub password)

**If you get "branch main doesn't exist" error:**
```bash
# Check current branch
git branch

# If you're on "master", either:
# Option A: Rename to main
git branch -M main
git push -u origin main

# Option B: Push to master
git push -u origin master
```

**If you get "rejected" error (repository has changes):**
```bash
# Force push (CAUTION: overwrites remote)
git push -f origin main
```

---

## 🔐 Creating GitHub Personal Access Token

If GitHub asks for password:

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Name: `CraftLens Deploy`
4. Expiration: `90 days` (or longer)
5. Scopes: Check **`repo`** (all sub-options)
6. Click **"Generate token"**
7. **COPY THE TOKEN** (you won't see it again!)
8. Use this as your password when git asks

---

## 💻 Method 2: Using GitHub Desktop (Easier)

### Step 1: Download GitHub Desktop
https://desktop.github.com

### Step 2: Install and Login
- Login with `Kaviya-0120`

### Step 3: Add Repository
1. File → Add Local Repository
2. Browse to: `C:\Users\kaviy\OneDrive\Desktop\Craftlens-main\Craftlens-main`
3. Click "Add Repository"

**If it says "not a git repository":**
- Click "Create a repository"
- Uncheck "Initialize with README"
- Click "Create Repository"

### Step 4: Publish to GitHub
1. Click **"Publish repository"**
2. Name: `craftLens1`
3. Uncheck "Keep this code private" (if you want public)
4. Click **"Publish repository"**

### Step 5: Verify
Go to: https://github.com/Kaviya-0120/craftLens1

You should see all your files!

---

## 🔍 Verify Your Push

### Check GitHub Repository
1. Visit: https://github.com/Kaviya-0120/craftLens1
2. You should see:
   ```
   ├── craftlens-backend/
   ├── craftlens-frontend/
   ├── RENDER_DEPLOY.md
   ├── LOCAL_RUN.md
   ├── GITHUB_PUSH.md
   └── README.md
   ```

### Verify Key Files
- ✅ `craftlens-backend/requirements.txt` (optimized version)
- ✅ `craftlens-backend/app/config.py` (with new settings)
- ✅ `craftlens-backend/app/services/asr_service.py` (Groq API support)
- ✅ `craftlens-backend/app/services/image_service.py` (remove.bg API)
- ❌ `.env` file should **NOT** be there (contains secrets!)

---

## 🔒 Security Check

### Ensure .env is NOT Pushed

Check your `.gitignore` file:
```bash
type .gitignore
# (Windows)

cat .gitignore
# (Mac/Linux)
```

Should contain:
```
.env
*.env
craftlens-backend/.env
venv/
node_modules/
__pycache__/
*.pyc
.DS_Store
```

**If .env was accidentally pushed:**

```bash
# Remove from git but keep local file
git rm --cached craftlens-backend/.env
git rm --cached .env

# Commit the removal
git commit -m "Remove .env file from repository"

# Push
git push origin main
```

---

## 🔄 Update Repository Later

After making changes:

```bash
# Check what changed
git status

# Add changes
git add .

# Commit with meaningful message
git commit -m "Your description here"

# Push to GitHub
git push origin main
```

---

## 🐛 Troubleshooting

### "fatal: not a git repository"
```bash
cd C:\Users\kaviy\OneDrive\Desktop\Craftlens-main\Craftlens-main
git init
```

### "Permission denied (publickey)"
Use HTTPS instead of SSH:
```bash
git remote set-url origin https://github.com/Kaviya-0120/craftLens1.git
```

### "Repository not found"
Check the URL is correct:
```bash
git remote -v
# Should show: https://github.com/Kaviya-0120/craftLens1.git
```

### "Updates were rejected"
```bash
# Pull first, then push
git pull origin main --rebase
git push origin main

# Or force push (careful!)
git push -f origin main
```

### "Large files detected"
GitHub has 100MB file limit. Check:
```bash
# Find large files
git ls-files -s | sort -n -k2

# Remove large file from git
git rm --cached path/to/large/file
```

### "Authentication failed"
- Use Personal Access Token (not password)
- Generate at: https://github.com/settings/tokens
- Use token as password when git prompts

---

## 📝 Git Workflow Summary

```bash
# 1. Check status
git status

# 2. Add files
git add .

# 3. Commit
git commit -m "Description of changes"

# 4. Push
git push origin main
```

---

## ✅ Success Checklist

- [ ] Repository accessible at: https://github.com/Kaviya-0120/craftLens1
- [ ] All folders visible (craftlens-backend, craftlens-frontend)
- [ ] .env file NOT visible (security!)
- [ ] README.md visible
- [ ] RENDER_DEPLOY.md visible
- [ ] requirements.txt shows optimized version
- [ ] Can clone repository from another location

---

## 🎯 Next Steps

After successful push:

1. ✅ **Verify on GitHub** - check all files uploaded
2. 🌐 **Deploy Backend** - follow RENDER_DEPLOY.md
3. 🎨 **Deploy Frontend** - follow RENDER_DEPLOY.md
4. 📱 **Test Mobile** - ensure camera/mic work on HTTPS
5. 🎉 **Share** - send link to artisans!

---

## 💡 Pro Tips

- **Commit often** with clear messages
- **Never commit** .env files or API keys
- **Use branches** for new features:
  ```bash
  git checkout -b feature-name
  git push origin feature-name
  ```
- **Pull before push** to avoid conflicts
- **Use .gitignore** to exclude unnecessary files

---

## 🆘 Need Help?

### Check Git Version
```bash
git --version
# Should be 2.x or higher
```

### Check Remote URL
```bash
git remote -v
# Should show your GitHub URL
```

### View Commit History
```bash
git log --oneline
# Shows recent commits
```

### Undo Last Commit (if needed)
```bash
# Keep changes
git reset --soft HEAD~1

# Discard changes
git reset --hard HEAD~1
```

---

Your code is now safely on GitHub! 🎉✨
