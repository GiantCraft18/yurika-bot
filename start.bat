@echo off
chcp 65001 >nul
title Yurika Bot

echo ========================================
echo  🤖 Запуск Yurika Bot
echo ========================================
echo.

cd /d "%~dp0"

if not exist Yurika.py (
    echo ❌ Файл Yurika.py не найден!
    echo 📌 Убедитесь, что Yurika.py находится в папке yurika-bot
    echo.
    pause
    exit /b
)

echo 🔍 Проверка токена...
findstr /C:"ваш_токен_lolka_здесь" Yurika.py >nul
if %errorlevel% == 0 (
    echo ⚠️ ВНИМАНИЕ: Токен не изменён!
    echo 📌 Замените 'ваш_токен_lolka_здесь' на реальный токен
    echo    в файле Yurika.py
    echo.
    choice /C YN /M "Продолжить запуск?"
    if errorlevel 2 exit /b
)

echo 🚀 Запуск бота...
echo.
C:\Users\Srazvorota161\AppData\Local\Programs\Python\Python314\python.exe Yurika.py

echo.
echo ========================================
echo  Бот остановлен
echo ========================================
pause