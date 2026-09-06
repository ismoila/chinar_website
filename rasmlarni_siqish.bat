@echo off
chcp 65001 >nul
title Rasmlarni siqish - Chinar
cd /d "%~dp0"

echo.
echo   ==========================================
echo      R A S M L A R N I   S I Q I S H
echo   ==========================================
echo.
echo   Bu dastur har bir rasmdan kichik nusxa yasaydi
echo   va media\cache papkasiga saqlaydi.
echo.
echo   ASL RASMLARINGIZGA TEGILMAYDI.
echo.
echo   Taxminan 15-40 daqiqa vaqt oladi.
echo   Oynani yopmang, kutib turing.
echo.
echo   Boshlash uchun tugmani bosing...
pause >nul
echo.

set PY=python
if exist "venv\Scripts\python.exe" set PY=venv\Scripts\python.exe

"%PY%" manage.py rasm_siqish
if errorlevel 1 (
    echo.
    echo   [X] Xato chiqdi. Yuqoridagi matnni menga yuboring.
)

echo.
echo   ------------------------------------------
echo   Tayyor. Endi saytni ishga tushirib koring.
echo   Tugmani bosing...
pause >nul
