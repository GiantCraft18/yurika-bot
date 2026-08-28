import lolka as discord
from lolka.ext import commands
import random
import asyncio
import datetime
import os
import math

# ===== ЗАГРУЗКА ТОКЕНА ИЗ .env =====
try:
    from dotenv import load_dotenv
    load_dotenv()
    TOKEN = os.getenv('LOLKA_TOKEN')
    print("✅ Токен загружен из .env файла")
except ImportError:
    print("⚠️ python-dotenv не установлен, используем прямой токен")
    TOKEN = "ваш_токен_lolka_здесь"
except Exception as e:
    print(f"⚠️ Ошибка загрузки .env: {e}")
    TOKEN = "ваш_токен_lolka_здесь"

# ===== НАСТРОЙКА =====

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
tree = bot.tree

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

def get_random_color():
    return random.randint(0, 0xFFFFFF)

def format_time(seconds):
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24
    if days > 0:
        return f"{days}д {hours % 24}ч"
    elif hours > 0:
        return f"{hours}ч {minutes % 60}м"
    elif minutes > 0:
        return f"{minutes}м {seconds % 60}с"
    else:
        return f"{seconds}с"

# ===== СОБЫТИЯ =====

@bot.event
async def on_ready():
    print(f"✅ Бот {bot.user} успешно запущен в Lolka!")
    print(f"📊 На серверах: {len(bot.guilds)}")
    
    for guild in bot.guilds:
        try:
            await tree.sync(guild=guild)
            print(f"🔄 Синхронизированы команды для сервера: {guild.name}")
        except Exception as e:
            print(f"❌ Ошибка синхронизации для {guild.name}: {e}")
    
    if len(bot.guilds) == 0:
        print("⚠️ Бот не добавлен ни на один сервер!")
    else:
        for guild in bot.guilds:
            print(f"   📌 Сервер: {guild.name} (ID: {guild.id})")
            print(f"   👥 Участников: {guild.member_count}")
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=f"/help | {len(bot.guilds)} серверов"
        )
    )

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Команда не найдена. Используйте `/help` или `!help`")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ У вас недостаточно прав для этой команды.")
    else:
        await ctx.send(f"❌ Ошибка: {error}")

@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name="Новичок")
    if role:
        await member.add_roles(role)
    channel = discord.utils.get(member.guild.channels, name="общий")
    if channel:
        await channel.send(f"👋 Добро пожаловать на сервер, {member.mention}!")

# ============================================
# ===== СЛЭШ-КОМАНДЫ =====
# ============================================

# --- ИНФОРМАЦИЯ ---

@tree.command(name="ping", description="Проверка задержки бота")
async def slash_ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    color = discord.Color.green() if latency < 50 else discord.Color.orange() if latency < 150 else discord.Color.red()
    embed = discord.Embed(title="🏓 Понг!", description=f"Задержка: **{latency}мс**", color=color)
    await interaction.response.send_message(embed=embed)

@tree.command(name="info", description="Информация о боте")
async def slash_info(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 Информация о боте", color=discord.Color.blue(), timestamp=datetime.datetime.now())
    embed.add_field(name="📛 Имя", value=bot.user.name, inline=True)
    embed.add_field(name="🆔 ID", value=bot.user.id, inline=True)
    embed.add_field(name="📊 Серверов", value=len(bot.guilds), inline=True)
    embed.add_field(name="👥 Всего пользователей", value=sum(g.member_count for g in bot.guilds), inline=True)
    embed.add_field(name="⌛ Задержка", value=f"{round(bot.latency * 1000)}мс", inline=True)
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(text="Используйте /help для списка команд")
    await interaction.response.send_message(embed=embed)

@tree.command(name="server", description="Информация о текущем сервере")
async def slash_server(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"📋 {guild.name}", color=discord.Color.blue())
    embed.add_field(name="👑 Владелец", value=guild.owner.mention, inline=True)
    embed.add_field(name="👥 Участников", value=guild.member_count, inline=True)
    embed.add_field(name="🤖 Ботов", value=sum(1 for m in guild.members if m.bot), inline=True)
    embed.add_field(name="📅 Создан", value=guild.created_at.strftime("%d.%m.%Y"), inline=True)
    embed.add_field(name="💬 Каналов", value=len(guild.channels), inline=True)
    embed.add_field(name="🎭 Ролей", value=len(guild.roles), inline=True)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await interaction.response.send_message(embed=embed)

@tree.command(name="user", description="Информация о пользователе")
async def slash_user(interaction: discord.Interaction, member: discord.Member = None):
    if member is None:
        member = interaction.user
    embed = discord.Embed(title=f"👤 {member.name}", color=get_random_color())
    embed.add_field(name="🆔 ID", value=member.id, inline=True)
    embed.add_field(name="📛 Ник", value=member.display_name, inline=True)
    embed.add_field(name="📅 Присоединился", value=member.joined_at.strftime("%d.%m.%Y %H:%M") if member.joined_at else "Неизвестно", inline=True)
    embed.add_field(name="📆 Аккаунт создан", value=member.created_at.strftime("%d.%m.%Y %H:%M"), inline=True)
    embed.add_field(name="🎭 Роли", value=", ".join([r.name for r in member.roles if r.name != "@everyone"]) or "Нет", inline=False)
    embed.add_field(name="🤖 Бот", value="✅" if member.bot else "❌", inline=True)
    embed.set_thumbnail(url=member.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@tree.command(name="avatar", description="Показать аватарку пользователя")
async def slash_avatar(interaction: discord.Interaction, member: discord.Member = None):
    if member is None:
        member = interaction.user
    embed = discord.Embed(title=f"🖼️ Аватар {member.name}", color=get_random_color())
    embed.set_image(url=member.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# --- ИГРЫ ---

@tree.command(name="roll", description="Бросить кубик")
async def slash_roll(interaction: discord.Interaction, max_num: int = 100):
    if max_num < 1:
        await interaction.response.send_message("❌ Число должно быть больше 0")
        return
    result = random.randint(1, max_num)
    embed = discord.Embed(title="🎲 Бросок кубика", description=f"Выпало: **{result}**", color=discord.Color.green())
    embed.add_field(name="Диапазон", value=f"1 - {max_num}", inline=True)
    await interaction.response.send_message(embed=embed)

@tree.command(name="coin", description="Орёл или решка?")
async def slash_coin(interaction: discord.Interaction):
    result = random.randint(0, 1)
    if result == 0:
        emoji, text = "🦅", "Орёл"
    else:
        emoji, text = "🪙", "Решка"
    embed = discord.Embed(title="🪙 Бросок монетки", description=f"{emoji} **{text}**!", color=discord.Color.gold())
    await interaction.response.send_message(embed=embed)

@tree.command(name="dice", description="Бросить 2 игральных кубика")
async def slash_dice(interaction: discord.Interaction):
    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    dice_faces = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
    embed = discord.Embed(title="🎲 Бросок двух кубиков", color=discord.Color.purple())
    embed.add_field(name="Первый кубик", value=f"{dice_faces[d1-1]} {d1}", inline=True)
    embed.add_field(name="Второй кубик", value=f"{dice_faces[d2-1]} {d2}", inline=True)
    embed.add_field(name="Сумма", value=f"**{d1 + d2}**", inline=True)
    await interaction.response.send_message(embed=embed)

@tree.command(name="rps", description="Камень, ножницы, бумага")
async def slash_rps(interaction: discord.Interaction, choice: str):
    choices = ["камень", "ножницы", "бумага"]
    if choice.lower() not in choices:
        await interaction.response.send_message("❌ Неверный выбор! Используйте: камень, ножницы или бумага")
        return
    bot_choice = random.randint(0, 2)
    bot_choice_name = choices[bot_choice]
    emoji_map = {"камень": "🪨", "ножницы": "✂️", "бумага": "📄"}
    user_index = choices.index(choice.lower())
    if user_index == bot_choice:
        result, color = "🤝 Ничья!", discord.Color.orange()
    elif (user_index == 0 and bot_choice == 1) or (user_index == 1 and bot_choice == 2) or (user_index == 2 and bot_choice == 0):
        result, color = "🎉 Вы победили!", discord.Color.green()
    else:
        result, color = "😔 Вы проиграли!", discord.Color.red()
    embed = discord.Embed(title="✊ Камень-ножницы-бумага", description=result, color=color)
    embed.add_field(name="Ваш выбор", value=f"{emoji_map[choice.lower()]} {choice.capitalize()}", inline=True)
    embed.add_field(name="Мой выбор", value=f"{emoji_map[bot_choice_name]} {bot_choice_name.capitalize()}", inline=True)
    await interaction.response.send_message(embed=embed)

@tree.command(name="guess", description="Угадай число от 1 до 10")
async def slash_guess(interaction: discord.Interaction):
    number = random.randint(1, 10)
    await interaction.response.send_message(f"🎯 Я загадал число от 1 до 10. Напишите число в чат!")
    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel and m.content.isdigit()
    try:
        msg = await bot.wait_for('message', timeout=30.0, check=check)
        guess_num = int(msg.content)
        if guess_num == number:
            await interaction.followup.send(f"🎉 Поздравляю! Вы угадали число **{number}**!")
        else:
            await interaction.followup.send(f"❌ Не угадали! Я загадал **{number}**, а вы назвали **{guess_num}**")
    except asyncio.TimeoutError:
        await interaction.followup.send(f"⏰ Время вышло! Я загадал **{number}**")

# --- УТИЛИТЫ ---

@tree.command(name="clear", description="Очистить сообщения")
@discord.app_commands.default_permissions(manage_messages=True)
async def slash_clear(interaction: discord.Interaction, amount: int = 5):
    if amount < 1 or amount > 100:
        await interaction.response.send_message("❌ Количество от 1 до 100")
        return
    await interaction.response.defer()
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"✅ Удалено {len(deleted)} сообщений")

@tree.command(name="timer", description="Установить таймер")
async def slash_timer(interaction: discord.Interaction, seconds: int = 10):
    if seconds < 5 or seconds > 600:
        await interaction.response.send_message("❌ Укажите время от 5 до 600 секунд")
        return
    embed = discord.Embed(title="⏰ Таймер", description=f"Запущен на **{seconds}** секунд", color=discord.Color.blue())
    embed.add_field(name="Пользователь", value=interaction.user.mention, inline=True)
    embed.add_field(name="Время", value=format_time(seconds), inline=True)
    await interaction.response.send_message(embed=embed)
    await asyncio.sleep(seconds)
    embed = discord.Embed(title="⏰ ТАЙМЕР", description=f"{interaction.user.mention}, время вышло!", color=discord.Color.red())
    embed.add_field(name="Прошло времени", value=format_time(seconds), inline=True)
    await interaction.followup.send(embed=embed)

@tree.command(name="random", description="Случайное число между a и b")
async def slash_random(interaction: discord.Interaction, a: int = 1, b: int = 100):
    if a > b:
        a, b = b, a
    if a == b:
        await interaction.response.send_message("❌ Числа должны быть разными")
        return
    result = random.randint(a, b)
    embed = discord.Embed(title="🎲 Случайное число", color=discord.Color.blue())
    embed.add_field(name="Диапазон", value=f"{a} - {b}", inline=True)
    embed.add_field(name="Результат", value=f"**{result}**", inline=True)
    await interaction.response.send_message(embed=embed)

@tree.command(name="calc", description="Калькулятор")
async def slash_calc(interaction: discord.Interaction, expression: str):
    try:
        allowed = set("0123456789+-*/().% ")
        if not all(c in allowed for c in expression):
            await interaction.response.send_message("❌ Недопустимые символы")
            return
        result = eval(expression)
        embed = discord.Embed(title="🧮 Калькулятор", color=discord.Color.green())
        embed.add_field(name="Выражение", value=f"`{expression}`", inline=False)
        embed.add_field(name="Результат", value=f"`{result}`", inline=False)
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Ошибка: {e}")

@tree.command(name="poll", description="Создать опрос")
async def slash_poll(interaction: discord.Interaction, question: str, option1: str, option2: str, option3: str = None, option4: str = None, option5: str = None):
    options = [o for o in [option1, option2, option3, option4, option5] if o]
    if len(options) < 2:
        await interaction.response.send_message("❌ Нужно минимум 2 варианта")
        return
    embed = discord.Embed(title="📊 Опрос", description=question, color=discord.Color.blue())
    emojis = ["🇦", "🇧", "🇨", "🇩", "🇪"]
    for i, option in enumerate(options):
        embed.add_field(name=f"{emojis[i]}", value=option, inline=True)
    embed.set_footer(text=f"Голосование от {interaction.user.name}")
    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    for i in range(len(options)):
        await msg.add_reaction(emojis[i])

# --- ЦИТАТЫ ---

@tree.command(name="quote", description="Цитата дня")
async def slash_quote(interaction: discord.Interaction):
    quotes = [
        "Жизнь - это то, что происходит, пока вы строите планы. © Джон Леннон",
        "Будь собой, все остальные роли уже заняты. © Оскар Уайльд",
        "Успех - это способность идти от неудачи к неудаче, не теряя энтузиазма. © Уинстон Черчилль",
        "Единственный способ делать великую работу - любить то, что вы делаете. © Стив Джобс",
        "Жизнь не в том, чтобы ждать, пока пройдет буря, а в том, чтобы научиться танцевать под дождем. © Вивиан Грин"
    ]
    embed = discord.Embed(title="💭 Цитата дня", description=f"*{random.choice(quotes)}*", color=discord.Color.gold())
    await interaction.response.send_message(embed=embed)

@tree.command(name="fact", description="Случайный факт")
async def slash_fact(interaction: discord.Interaction):
    facts = [
        "🐱 Кошки спят до 16 часов в день",
        "🌊 Океан покрывает 71% поверхности Земли",
        "🍕 Самая большая пицца была диаметром 37 метров",
        "📱 Первый смартфон был создан в 1992 году",
        "🌍 В Антарктиде есть город с населением 300 человек",
        "🦷 Улитки имеют около 25 000 зубов",
        "🐧 Пингвины могут пить соленую воду",
        "🍄 Грибы ближе к животным, чем к растениям"
    ]
    embed = discord.Embed(title="📖 Интересный факт", description=random.choice(facts), color=discord.Color.blue())
    await interaction.response.send_message(embed=embed)

# --- РАЗВЛЕЧЕНИЯ ---

@tree.command(name="joke", description="Случайная шутка")
async def slash_joke(interaction: discord.Interaction):
    jokes = [
        "Почему программисты путают Хэллоуин и Рождество? Потому что 31 Oct = 25 Dec!",
        "Сколько программистов нужно, чтобы заменить лампочку? Ни одного, это проблема 'железа'!",
        "Что сказал 0 числу 8? Хороший ремешок!",
        "Почему слон не умеет программировать? Он боится 'мышей'!",
        "Как узнать, что программист экстраверт? Он смотрит на твои ботинки, а не на свои!"
    ]
    embed = discord.Embed(title="😂 Шутка дня", description=random.choice(jokes), color=discord.Color.green())
    await interaction.response.send_message(embed=embed)

@tree.command(name="say", description="Повторить сообщение")
async def slash_say(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(f"💬 {message}")

@tree.command(name="rate", description="Оценить что-либо от 0 до 10")
async def slash_rate(interaction: discord.Interaction, thing: str = "Жизнь"):
    rating = random.randint(0, 10)
    embed = discord.Embed(title="⭐ Оценка", color=discord.Color.gold())
    embed.add_field(name="Объект", value=thing, inline=True)
    embed.add_field(name="Оценка", value=f"{rating}/10", inline=True)
    if rating >= 8:
        embed.description = "🌟 Отлично!"
    elif rating >= 5:
        embed.description = "👍 Неплохо!"
    else:
        embed.description = "👎 Могло быть и лучше..."
    await interaction.response.send_message(embed=embed)

# --- МОДЕРАЦИЯ ---

@tree.command(name="kick", description="Выгнать участника")
@discord.app_commands.default_permissions(kick_members=True)
async def slash_kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Не указана"):
    if member == interaction.user:
        await interaction.response.send_message("❌ Нельзя выгнать самого себя!")
        return
    embed = discord.Embed(title="👢 Kick", color=discord.Color.orange())
    embed.add_field(name="Участник", value=member.mention, inline=True)
    embed.add_field(name="Модератор", value=interaction.user.mention, inline=True)
    embed.add_field(name="Причина", value=reason, inline=False)
    await member.kick(reason=reason)
    await interaction.response.send_message(embed=embed)

@tree.command(name="ban", description="Забанить участника")
@discord.app_commands.default_permissions(ban_members=True)
async def slash_ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Не указана"):
    if member == interaction.user:
        await interaction.response.send_message("❌ Нельзя забанить самого себя!")
        return
    embed = discord.Embed(title="🔨 Ban", color=discord.Color.red())
    embed.add_field(name="Участник", value=member.mention, inline=True)
    embed.add_field(name="Модератор", value=interaction.user.mention, inline=True)
    embed.add_field(name="Причина", value=reason, inline=False)
    await member.ban(reason=reason)
    await interaction.response.send_message(embed=embed)

@tree.command(name="mute", description="Заглушить участника")
@discord.app_commands.default_permissions(moderate_members=True)
async def slash_mute(interaction: discord.Interaction, member: discord.Member, minutes: int = 10):
    if minutes < 1 or minutes > 1440:
        await interaction.response.send_message("❌ Время от 1 до 1440 минут")
        return
    await member.timeout(datetime.timedelta(minutes=minutes))
    await interaction.response.send_message(f"🔇 {member.mention} заглушен на {minutes} минут")

@tree.command(name="lock", description="Закрыть канал")
@discord.app_commands.default_permissions(manage_channels=True)
async def slash_lock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 Канал закрыт")

@tree.command(name="unlock", description="Открыть канал")
@discord.app_commands.default_permissions(manage_channels=True)
async def slash_unlock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("🔓 Канал открыт")

# --- СТАТИСТИКА ---

@tree.command(name="stats", description="Статистика бота")
async def slash_stats(interaction: discord.Interaction):
    embed = discord.Embed(title="📊 Статистика бота", color=discord.Color.blue())
    embed.add_field(name="👥 Серверов", value=len(bot.guilds), inline=True)
    embed.add_field(name="👤 Пользователей", value=sum(g.member_count for g in bot.guilds), inline=True)
    embed.add_field(name="⚡ Задержка", value=f"{round(bot.latency * 1000)}мс", inline=True)
    embed.add_field(name="📝 Команд", value=len(tree.get_commands()), inline=True)
    embed.add_field(name="⏱️ Запущен", value=datetime.datetime.now().strftime("%d.%m.%Y %H:%M"), inline=True)
    await interaction.response.send_message(embed=embed)

# --- HELP ---

@tree.command(name="help", description="Показать список всех команд")
async def slash_help(interaction: discord.Interaction, command: str = None):
    if command:
        cmd = bot.get_command(command)
        if cmd:
            embed = discord.Embed(title=f"📖 {cmd.name}", description=cmd.help or "Нет описания", color=discord.Color.blue())
            embed.add_field(name="Использование", value=f"/{cmd.name}", inline=False)
            await interaction.response.send_message(embed=embed)
            return
        else:
            await interaction.response.send_message(f"❌ Команда `{command}` не найдена")
            return
    
    embed = discord.Embed(title="🤖 Список команд", description="Все команды доступны через `/`:", color=discord.Color.green())
    categories = {
        "📊 Информация": ["ping", "info", "server", "user", "avatar"],
        "🎮 Игры": ["roll", "coin", "dice", "rps", "guess"],
        "🔧 Утилиты": ["clear", "timer", "random", "calc", "poll"],
        "💭 Цитаты": ["quote", "fact"],
        "😂 Развлечения": ["joke", "say", "rate"],
        "🛡️ Модерация": ["kick", "ban", "mute", "lock", "unlock"],
        "📊 Статистика": ["stats"]
    }
    for category, commands_list in categories.items():
        value = "\n".join([f"  • `/{cmd}`" for cmd in commands_list])
        embed.add_field(name=category, value=value, inline=False)
    embed.set_footer(text="Введите / и название команды")
    await interaction.response.send_message(embed=embed)

# ============================================
# ===== ТЕКСТОВЫЕ КОМАНДЫ (для совместимости) =====
# ============================================

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Понг! Задержка: {latency}мс")

@bot.command()
async def info(ctx):
    embed = discord.Embed(title="🤖 Информация о боте", color=discord.Color.blue())
    embed.add_field(name="📛 Имя", value=bot.user.name, inline=True)
    embed.add_field(name="📊 Серверов", value=len(bot.guilds), inline=True)
    embed.add_field(name="👥 Пользователей", value=sum(g.member_count for g in bot.guilds), inline=True)
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def server(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"📋 {guild.name}", color=discord.Color.blue())
    embed.add_field(name="👑 Владелец", value=guild.owner.mention, inline=True)
    embed.add_field(name="👥 Участников", value=guild.member_count, inline=True)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await ctx.send(embed=embed)

@bot.command()
async def user(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    embed = discord.Embed(title=f"👤 {member.name}", color=get_random_color())
    embed.add_field(name="🆔 ID", value=member.id, inline=True)
    embed.add_field(name="📛 Ник", value=member.display_name, inline=True)
    embed.add_field(name="🤖 Бот", value="✅" if member.bot else "❌", inline=True)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    embed = discord.Embed(title=f"🖼️ Аватар {member.name}", color=get_random_color())
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def roll(ctx, max_num: int = 100):
    if max_num < 1:
        await ctx.send("❌ Число должно быть больше 0")
        return
    result = random.randint(1, max_num)
    await ctx.send(f"🎲 Выпало: **{result}** (1-{max_num})")

@bot.command()
async def coin(ctx):
    result = random.randint(0, 1)
    await ctx.send(f"🪙 **{'Орёл 🦅' if result == 0 else 'Решка'}**!")

@bot.command()
async def dice(ctx):
    d1, d2 = random.randint(1, 6), random.randint(1, 6)
    await ctx.send(f"🎲 {d1} + {d2} = **{d1 + d2}**")

@bot.command()
async def rps(ctx, choice: str = None):
    if choice is None:
        await ctx.send("❌ Выберите: **камень**, **ножницы** или **бумага**")
        return
    choices = ["камень", "ножницы", "бумага"]
    if choice.lower() not in choices:
        await ctx.send("❌ Неверный выбор! Используйте: камень, ножницы или бумага")
        return
    bot_choice = random.randint(0, 2)
    bot_choice_name = choices[bot_choice]
    emoji_map = {"камень": "🪨", "ножницы": "✂️", "бумага": "📄"}
    user_index = choices.index(choice.lower())
    if user_index == bot_choice:
        result = "🤝 Ничья!"
    elif (user_index == 0 and bot_choice == 1) or (user_index == 1 and bot_choice == 2) or (user_index == 2 and bot_choice == 0):
        result = "🎉 Вы победили!"
    else:
        result = "😔 Вы проиграли!"
    await ctx.send(f"{result}\nВаш выбор: {emoji_map[choice.lower()]} {choice.capitalize()}\nМой выбор: {emoji_map[bot_choice_name]} {bot_choice_name.capitalize()}")

@bot.command()
async def guess(ctx):
    number = random.randint(1, 10)
    await ctx.send(f"🎯 Я загадал число от 1 до 10. Напишите число в чат!")
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()
    try:
        msg = await bot.wait_for('message', timeout=30.0, check=check)
        guess_num = int(msg.content)
        if guess_num == number:
            await ctx.send(f"🎉 Поздравляю! Вы угадали число **{number}**!")
        else:
            await ctx.send(f"❌ Не угадали! Я загадал **{number}**, а вы назвали **{guess_num}**")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ Время вышло! Я загадал **{number}**")

@bot.command()
async def clear(ctx, amount: int = 5):
    if amount < 1 or amount > 100:
        await ctx.send("❌ Количество от 1 до 100")
        return
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("❌ У вас нет прав!")
        return
    deleted = await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"✅ Удалено {len(deleted) - 1} сообщений")
    await asyncio.sleep(3)
    await msg.delete()

@bot.command()
async def timer(ctx, seconds: int = 10):
    if seconds < 5 or seconds > 600:
        await ctx.send("❌ От 5 до 600 секунд")
        return
    await ctx.send(f"⏰ Таймер на {seconds} секунд")
    await asyncio.sleep(seconds)
    await ctx.send(f"⏰ {ctx.author.mention}, время вышло!")

@bot.command()
async def random_num(ctx, a: int = 1, b: int = 100):
    if a > b:
        a, b = b, a
    result = random.randint(a, b)
    await ctx.send(f"🎲 Случайное число: **{result}** ({a}-{b})")

@bot.command()
async def calc(ctx, *, expression: str):
    try:
        allowed = set("0123456789+-*/().% ")
        if not all(c in allowed for c in expression):
            await ctx.send("❌ Недопустимые символы")
            return
        result = eval(expression)
        await ctx.send(f"🧮 `{expression}` = **{result}**")
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {e}")

@bot.command()
async def poll(ctx, question: str, *options):
    if len(options) < 2:
        await ctx.send("❌ Нужно минимум 2 варианта")
        return
    embed = discord.Embed(title="📊 Опрос", description=question, color=discord.Color.blue())
    emojis = ["🇦", "🇧", "🇨", "🇩", "🇪"]
    for i, option in enumerate(options[:5]):
        embed.add_field(name=f"{emojis[i]}", value=option, inline=True)
    embed.set_footer(text=f"Голосование от {ctx.author.name}")
    msg = await ctx.send(embed=embed)
    for i in range(min(len(options), 5)):
        await msg.add_reaction(emojis[i])

@bot.command()
async def quote(ctx):
    quotes = [
        "Жизнь - это то, что происходит, пока вы строите планы. © Джон Леннон",
        "Будь собой, все остальные роли уже заняты. © Оскар Уайльд",
        "Успех - это способность идти от неудачи к неудаче, не теряя энтузиазма. © Уинстон Черчилль"
    ]
    await ctx.send(f"💭 {random.choice(quotes)}")

@bot.command()
async def fact(ctx):
    facts = [
        "🐱 Кошки спят до 16 часов в день",
        "🌊 Океан покрывает 71% поверхности Земли",
        "🍕 Самая большая пицца была диаметром 37 метров"
    ]
    await ctx.send(f"📖 {random.choice(facts)}")

@bot.command()
async def joke(ctx):
    jokes = [
        "Почему программисты путают Хэллоуин и Рождество? Потому что 31 Oct = 25 Dec!",
        "Сколько программистов нужно, чтобы заменить лампочку? Ни одного, это проблема 'железа'!"
    ]
    await ctx.send(f"😂 {random.choice(jokes)}")

@bot.command()
async def say(ctx, *, message: str):
    await ctx.send(f"💬 {message}")

@bot.command()
async def rate(ctx, *, thing: str = "Жизнь"):
    rating = random.randint(0, 10)
    text = "🌟 Отлично!" if rating >= 8 else "👍 Неплохо!" if rating >= 5 else "👎 Могло быть лучше..."
    await ctx.send(f"⭐ {thing}: **{rating}/10** — {text}")

@bot.command()
async def help(ctx, command: str = None):
    if command:
        cmd = bot.get_command(command)
        if cmd:
            await ctx.send(f"📖 {cmd.name}: {cmd.help or 'Нет описания'}")
            return
        await ctx.send(f"❌ Команда {command} не найдена")
        return
    embed = discord.Embed(title="🤖 Команды бота", color=discord.Color.green())
    categories = {
        "📊 Информация": ["ping", "info", "server", "user", "avatar"],
        "🎮 Игры": ["roll", "coin", "dice", "rps", "guess"],
        "🔧 Утилиты": ["clear", "timer", "random_num", "calc", "poll"],
        "💭 Цитаты": ["quote", "fact"],
        "😂 Развлечения": ["joke", "say", "rate"],
        "🛡️ Модерация": ["kick", "ban", "mute", "lock", "unlock"]
    }
    for category, commands_list in categories.items():
        value = ", ".join([f"`!{cmd}`" for cmd in commands_list])
        embed.add_field(name=category, value=value, inline=False)
    embed.set_footer(text="Используйте !help [команда] для подробностей")
    await ctx.send(embed=embed)

@bot.command()
@commands.is_owner()
async def sync(ctx):
    try:
        await tree.sync(guild=ctx.guild)
        await ctx.send(f"✅ Команды синхронизированы для сервера {ctx.guild.name}!")
    except Exception as e:
        await ctx.send(f"❌ Ошибка синхронизации: {e}")

# ============================================
# ===== ЗАПУСК =====
# ============================================

if __name__ == "__main__":
    if not TOKEN or TOKEN == "ваш_токен_lolka_здесь":
        print("❌ Ошибка: Токен не установлен!")
        print("📌 Создайте файл .env в папке с ботом")
        print("📌 Добавьте в него: LOLKA_TOKEN=ваш_токен")
        print("📌 Или замените 'ваш_токен_lolka_здесь' на реальный токен")
    else:
        try:
            print("🔄 Запуск бота...")
            bot.run(TOKEN)
        except Exception as e:
            print(f"❌ Ошибка: {e}")