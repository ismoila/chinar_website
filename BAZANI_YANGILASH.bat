@echo off
chcp 65001 >nul
title Bazani yangilash - Chinar
cd /d "%~dp0"

echo.
echo   ==========================================
echo      B A Z A N I   Y A N G I L A S H
echo   ==========================================
echo.
echo   Mahsulotlarga uchta yangi maydon qoshiladi:
echo     - Tavsif      (ixtiyoriy matn)
echo     - Material    (ixtiyoriy)
echo     - Sotuvda bor (belgi, standart: bor)
echo.
echo   Mavjud malumotlarga TEGILMAYDI.
echo.
echo   Boshlash uchun tugmani bosing...
pause >nul
echo.

set PY=python
if exist "venv\Scripts\python.exe" set PY=venv\Scripts\python.exe

"%PY%" manage.py migrate
if errorlevel 1 (
    echo.
    echo   [X] Xato chiqdi. Yuqoridagi matnni menga yuboring.
    goto son
)

echo.
echo   [ok] Tayyor. Admin panelda mahsulotlar royxatida
echo        "Sotuvda bor" ustuni paydo boladi - belgini
echo        olib tashlasangiz saytda "Vaqtincha yoq" deb chiqadi.

:son
echo.
echo   Tugmani bosing...
pause >nul
