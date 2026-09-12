@echo off
echo ====================================
echo CraftLens - Push to GitHub
echo ====================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed!
    echo Please install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [1/5] Checking current directory...
cd /d "%~dp0"
echo Current directory: %CD%
echo.

echo [2/5] Checking git status...
git status
echo.

echo [3/5] Adding all files to git...
git add .
echo Files staged for commit
echo.

echo [4/5] Creating commit...
set /p commit_message="Enter commit message (or press Enter for default): "
if "%commit_message%"=="" set commit_message=Update CraftLens - optimized for free tier deployment

git commit -m "%commit_message%"
echo.

echo [5/5] Pushing to GitHub...
echo Attempting to push to: https://github.com/Kaviya-0120/craftLens1.git

REM Check if remote exists
git remote -v | find "origin" >nul
if %errorlevel% neq 0 (
    echo Adding remote repository...
    git remote add origin https://github.com/Kaviya-0120/craftLens1.git
)

REM Try to push
git push -u origin main
if %errorlevel% neq 0 (
    echo.
    echo Push failed! Trying alternative branch name...
    git push -u origin master
    if %errorlevel% neq 0 (
        echo.
        echo ====================================
        echo ERROR: Push failed!
        echo ====================================
        echo.
        echo Possible reasons:
        echo 1. Authentication failed (use Personal Access Token)
        echo 2. Repository doesn't exist
        echo 3. No internet connection
        echo.
        echo To get Personal Access Token:
        echo 1. Go to: https://github.com/settings/tokens
        echo 2. Generate new token (classic)
        echo 3. Copy the token
        echo 4. Use it as password when git asks
        echo.
        pause
        exit /b 1
    )
)

echo.
echo ====================================
echo SUCCESS! Code pushed to GitHub
echo ====================================
echo.
echo View your repository at:
echo https://github.com/Kaviya-0120/craftLens1
echo.
echo Next steps:
echo 1. Verify files on GitHub
echo 2. Follow RENDER_DEPLOY.md to deploy backend
echo 3. Deploy frontend to Vercel
echo.
pause
