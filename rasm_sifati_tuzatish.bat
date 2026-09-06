@echo off
chcp 65001 >nul
title Rasm sifatini tuzatish - Chinar
cd /d "%~dp0"

echo.
echo   ==========================================
echo      R A S M   S I F A T I N I   T U Z A T I S H
echo   ==========================================
echo.
echo   Katta rasmlar sifati oshiriladi (82 -^> 90)
echo   va zoom uchun 2000px nusxa yasaladi.
echo.
echo   Kichik nusxalar (200, 600) o'zgarmaydi.
echo   Taxminan 8-15 daqiqa.
echo.
echo   Boshlash uchun tugmani bosing...
pause >nul
echo.

set PY=python
if exist "venv\Scripts\python.exe" set PY=venv\Scripts\python.exe

"%PY%" manage.py rasm_siqish --kengliklar 1200,2000 --qayta
if errorlevel 1 (
    echo.
    echo   [X] Xato chiqdi. Yuqoridagi matnni menga yuboring.
)

echo.
echo   ------------------------------------------
echo   Tayyor. Saytni qayta ishga tushiring.
echo   Tugmani bosing...
pause >nul
