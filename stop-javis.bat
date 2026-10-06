@echo off
REM CAU NOI cho may Windows cai TRUOC Thansa 1.19 - KHONG sua, KHONG xoa.
REM Updater ban cu goi dich danh file nay. File that nay la stop-thansa.bat.
call "%~dp0stop-thansa.bat"
exit /b %errorlevel%
