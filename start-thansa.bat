@echo off
chcp 65001 >nul
title Khoi dong Thansa OS
cd /d "%~dp0"

echo Bat Thansa OS chay NEN - khong con cua so den (port 7777)...
REM Viec tat instance cu + chay server AN giao het cho start-thansa.vbs (cua so an hoan toan).
REM Log ghi vao server\thansa.log (mo file do neu can xem loi). Tat server: stop-thansa.bat.
wscript //nologo start-thansa.vbs

echo.
echo Da bat. Cho ~10 giay roi mo http://localhost:7777 va bam Ctrl+Shift+R.
echo (Tat server: chay stop-thansa.bat. Xem loi: mo file server\thansa.log)
timeout /t 4 >nul
