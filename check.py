"""
Проверка установленных библиотек для Yurika Bot
"""

print("=" * 50)
print("  🔍 Проверка установленных библиотек")
print("=" * 50)
print()

# Список библиотек для проверки
libraries = [
    ("yt_dlp", "yt-dlp"),
    ("bs4", "beautifulsoup4"),
    ("aiohttp", "aiohttp"),
    ("PIL", "pillow"),
    ("psutil", "psutil"),
    ("dotenv", "python-dotenv"),
    ("lolka", "lolka-py"),
    ("requests", "requests"),
    ("numpy", "numpy")
]

installed = []
not_installed = []

for module_name, package_name in libraries:
    try:
        if module_name == "PIL":
            import PIL
            version = PIL.__version__
        elif module_name == "lolka":
            import lolka
            version = lolka.__version__
        else:
            module = __import__(module_name)
            version = getattr(module, "__version__", "неизвестно")
        
        installed.append((package_name, version))
        print(f"✅ {package_name:20} — установлена (v{version})")
    except ImportError:
        not_installed.append(package_name)
        print(f"❌ {package_name:20} — НЕ УСТАНОВЛЕНА")

print()
print("=" * 50)

if not_installed:
    print("⚠️ Отсутствуют библиотеки:")
    for lib in not_installed:
        print(f"   • {lib}")
    print()
    print("📌 Установите их командой:")
    print(f"   python -m pip install {' '.join(not_installed)}")
else:
    print("✅ Все библиотеки успешно установлены!")

print("=" * 50)
print()
print(f"📊 Всего библиотек: {len(installed)}")
print(f"✅ Установлено: {len(installed)}")
print(f"❌ Отсутствует: {len(not_installed)}")