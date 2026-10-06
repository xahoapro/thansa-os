@echo off
chcp 65001 >nul
title Tu khoi dong Thansa OS
REM Tu khoi dong Thansa cung Windows. Dung: thansa-autostart.bat install | uninstall | status
REM Logic nam trong thansa-autostart.ps1 (ghi/xoa muc ThansaOS trong HKCU Run, khong can quyen
REM admin). Bat roi thi dang nhap may la server tu chay nen va tu mo dashboard (0.306.0).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0thansa-autostart.ps1" %1
