@echo off
chcp 65001 >nul
title Tu khoi dong Thansa OS
REM Tu khoi dong Thansa cung Windows. Dung: thansa-autostart.bat install | uninstall | status
REM Logic nam trong thansa-autostart.ps1 (tao/xoa shortcut trong thu muc Startup cua user,
REM khong can quyen admin). Bat roi thi dang nhap may la server tu chay nen.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0thansa-autostart.ps1" %1
