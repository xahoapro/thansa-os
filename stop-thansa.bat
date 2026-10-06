@echo off
chcp 65001 >nul
title Dung Thansa OS
echo Dang tim va tat Thansa OS...
REM Logic giet nam trong stop-thansa.ps1 (giet theo dung python cua venv + chu port 7777).
REM KHONG dung timeout o day: chay an qua VBS se loi "Input redirection is not supported".
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0stop-thansa.ps1"
REM Don cua so CMD den "Thansa OS" kieu cu con sot (flow moi chay an, khong tao cua so nay).
taskkill /F /FI "IMAGENAME eq cmd.exe" /FI "WINDOWTITLE eq Thansa OS*" >nul 2>&1
REM May cai truoc 1.19: cua so cu mang tieu de "Javis OS".
taskkill /F /FI "IMAGENAME eq cmd.exe" /FI "WINDOWTITLE eq Javis OS*" >nul 2>&1
echo Xong.
exit /b 0
