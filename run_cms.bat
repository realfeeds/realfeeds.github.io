@echo off
echo Starting CMS...
echo Please leave this window open while you are adding projects.
start http://localhost:8080
python cms_server.py
pause
