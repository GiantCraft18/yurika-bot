@echo off
chcp 65001 >nul
title Установка библиотек для Yurika Bot

echo ========================================
echo  📦 Установка библиотек для Yurika Bot
echo ========================================
echo.

cd /d "%~dp0"

if not exist requirements.txt (
    echo ❌ Файл requirements.txt не найден!
    echo 📌 Создайте файл requirements.txt в папке yurika-bot
    echo.
    pause
    exit /b
)

echo 📋 Устанавливаемые библиотеки:
echo.
type requirements.txt
echo.
echo ========================================
echo.

echo ⏳ Обновление pip...
C:\Users\Srazvorota161\AppData\Local\Programs\Python\Python314\python.exe -m pip install --upgrade pip
echo.

echo ⏳ Установка библиотек...
C:\Users\Srazvorota161\AppData\Local\Programs\Python\Python314\python.exe -m pip install -r requirements.txt

if %errorlevel% == 0 (
    echo.
    echo ========================================
    echo  ✅ Установка завершена успешно!
    echo ========================================
    echo.
    echo 📊 Установленные библиотеки:
    C:\Users\Srazvorota161\AppData\Local\Programs\Python\Python314\python.exe -m pip list
) else (
    echo.
    echo ========================================
    echo  ❌ Ошибка при установке библиотек!
    echo ========================================
)

echo.
pause