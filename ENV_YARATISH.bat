@echo off
chcp 65001 >nul
title .env yaratish - Chinar
cd /d "%~dp0"

echo.
echo   ==========================================
echo      . E N V   F A Y L I N I   Y A R A T I S H
echo   ==========================================
echo.

if not exist "kalitlar_env.txt" (
    echo   [X] kalitlar_env.txt topilmadi.
    echo       Bu faylni chinar_website papkasiga qoying.
    goto son
)

if exist ".env" (
    echo   [!] .env fayli allaqachon bor.
    echo       Eskisi .env.eski nomi bilan saqlanadi.
    copy /Y ".env" ".env.eski" >nul
)

copy /Y "kalitlar_env.txt" ".env" >nul
if errorlevel 1 (
    echo   [X] .env yaratilmadi.
    goto son
)
echo   [ok] .env yaratildi

if exist "env_namuna.txt" (
    copy /Y "env_namuna.txt" ".env.namuna" >nul
    del "env_namuna.txt" >nul 2>&1
    echo   [ok] .env.namuna yaratildi
)

del "kalitlar_env.txt" >nul 2>&1
echo   [ok] Vaqtinchalik fayl ochirildi

echo.
echo   Tekshirilmoqda...
set PY=python
if exist "venv\Scripts\python.exe" set PY=venv\Scripts\python.exe
"%PY%" -c "import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings');django.setup();from django.conf import settings as S;print('   Telegram kaliti:', 'BOR' if len(S.TELEGRAM_BOT_TOKEN)>20 else 'YOQ');print('   SMS kaliti     :', 'BOR' if len(S.DEVSMS_TOKEN)>20 else 'YOQ');print('   SECRET_KEY     :', 'BOR' if 'insecure-faqat' not in S.SECRET_KEY else 'YOQ')"

echo.
echo   ------------------------------------------
echo   Tayyor. Endi saytni ishga tushiring.
:son
echo.
echo   Tugmani bosing...
pause >nul
