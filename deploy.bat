@echo off
echo ==============================================
echo      Deploying Website to GitHub Pages...
echo ==============================================
echo.

:: Stage all changes
git add .

:: Commit with a simple timestamped message
git commit -m "Auto-deploy update"

:: Push to remote
echo.
echo Pushing changes to GitHub...
git push origin main

echo.
echo ==============================================
echo  Done! Your website will be live in 1-2 mins.
echo ==============================================
pause
