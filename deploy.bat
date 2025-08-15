@echo off
echo 正在初始化Git仓库...
git init
git add .
git commit -m "Initial commit: Realtime Audio Translation Tool"
echo.
echo 请手动添加远程仓库并推送:
echo git remote add origin ^<your-repo-url^>
echo git push -u origin main
pause
