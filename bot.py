import sqlite3
from vkbottle.bot import Bot, Message
import re
from database import add_user, get_balance, update_balance
from shop import SHOP
from database import get_db_connection

TOKEN = "vk1.a.dAqeMkcX_NKGA4yshYUCrB2mNhoxoLK3fJWxBbf3oWlUfv50YQ3371dAqmAEbXOmwyASe0QhtRiw4VaJhxdXCMcpK32Pq9h9DpX_e_OkBjy1By5E2XnmkFEYNN04VmLLzuVG7SV_ga10jOZv0hq64Gb1mBXHN_JojVvgkinqGbZbfQuxabYnsBTM0N0CvaadAt2uo-_q7WDPOAlIwS1HSg"
ADMINS = [527055305]  # Список администраторов

# Инициализация бота
bot = Bot(TOKEN)

# Функция для получения имени пользователя по ID
async def get_user_name(user_id: int) -> str:
    # Получаем информацию о пользователе
    user_info = await bot.api.users.get(user_ids=user_id)
    user = user_info[0]  # Пользовательский объект
    return f"{user.first_name} {user.last_name}"

@bot.on.message(text="/руководство")
async def staff_handler(message: Message):
    staff = get_staff()
    if not staff:
        await message.reply("Список сотрудников пуст.")
        return

    staff_text = "📋 Список сотрудников:\n"
    roles = {
        "owner": "Главный модератор",
        "chief": "Главный модератор 75",
        "zgm": "Зам.Главного модератора",
        "cur": "Куратор модерации"
    }

    for role, description in roles.items():
        staff_text += f"\n🔹 {description}:\n"
        for user_id, user_role in staff:
            if user_role == role:
                user_name = await get_user_name(user_id)  # Получаем имя пользователя
                staff_text += f"  [https://vk.com/id{user_id}|{user_name}]\n"

    await message.reply(staff_text)

# Извлечение ID пользователя из упоминания
async def get_user_id_from_mention(message: Message, mention: str) -> int:
    match = re.match(r"\[id(\d+)\|", mention)
    if match:
        return int(match.group(1))
    if mention.isdigit():
        return int(mention)
    return None

def get_db_connection():
    conn = sqlite3.connect('C:\\Users\\Asus\\vk_bot\\database.db')  # Укажите путь к вашей базе данных
    return conn

# Определим приоритет ролей для проверки
ROLE_PRIORITY = {
    "owner": 5,
    "chief": 4,
    "zgm": 3,
    "cur": 2,
    "user": 1
}

# Функция для проверки, может ли пользователь выдать роль
def can_assign_role(current_role, target_role):
    return ROLE_PRIORITY[current_role] > ROLE_PRIORITY[target_role]

# Функция для получения роли пользователя из базы данных
def get_user_role(user_id):
    conn = sqlite3.connect('C:\\Users\\Asus\\vk_bot\\database.db')  # Укажите путь к вашей базе данных
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "user"  # Если роли нет, то возвращаем "user"

# Функция для обновления роли пользователя
def set_role(user_id, role, current_user_role):
    if not can_assign_role(current_user_role, role):
        return False  # Если у текущего пользователя роль ниже, отказать
    
    conn = sqlite3.connect('C:\\Users\\Asus\\vk_bot\\database.db')  # Укажите путь к вашей базе данных
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (user_id, role) VALUES (?, ?)", (user_id, role))
    conn.commit()
    conn.close()
    return True

# Функция для получения всех сотрудников
def get_staff():
    conn = sqlite3.connect('C:\\Users\\Asus\\vk_bot\\database.db')  # Укажите путь к вашей базе данных
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, role FROM users")
    staff = cursor.fetchall()
    conn.close()
    return staff

# Команда для выдачи роли через упоминание
@bot.on.message(text="/addowner <mention>")
async def add_owner_handler(message: Message, mention: str):
    user_id = message.from_id  # ID пользователя, который отправил команду
    target_user_id = await get_user_id_from_mention(message, mention)  # ID пользователя, которого упомянули

    if not target_user_id:
        await message.answer("⛔ Не удалось найти пользователя в упоминании.")
        return

    current_user_role = get_user_role(user_id)  # Получаем роль текущего пользователя
    if set_role(target_user_id, "owner", current_user_role):
        await message.answer(f"Вы назначили [id{target_user_id}|пользователя] владельцем беседы.")
    else:
        await message.answer("⛔ У вас недостаточно прав для назначения этой роли.")

# Команда для выдачи роли главного модератора через упоминание
@bot.on.message(text="/addchief <mention>")
async def add_chief_handler(message: Message, mention: str):
    user_id = message.from_id
    target_user_id = await get_user_id_from_mention(message, mention)

    if not target_user_id:
        await message.answer("⛔ Не удалось найти пользователя в упоминании.")
        return

    current_user_role = get_user_role(user_id)
    if set_role(target_user_id, "chief", current_user_role):
        await message.answer(f"Вы назначили [id{target_user_id}|пользователя] главным модератором (75).")
    else:
        await message.answer("⛔ У вас недостаточно прав для назначения этой роли.")

# Команда для выдачи роли заместителя главного модератора через упоминание
@bot.on.message(text="/addzgm <mention>")
async def add_zgm_handler(message: Message, mention: str):
    user_id = message.from_id
    target_user_id = await get_user_id_from_mention(message, mention)

    if not target_user_id:
        await message.answer("⛔ Не удалось найти пользователя в упоминании.")
        return

    current_user_role = get_user_role(user_id)
    if set_role(target_user_id, "zgm", current_user_role):
        await message.answer(f"Вы назначили [id{target_user_id}|пользователя] заместителем главного модератора.")
    else:
        await message.answer("⛔ У вас недостаточно прав для назначения этой роли.")

# Команда для выдачи роли куратора через упоминание
@bot.on.message(text="/addcur <mention>")
async def add_cur_handler(message: Message, mention: str):
    user_id = message.from_id
    target_user_id = await get_user_id_from_mention(message, mention)

    if not target_user_id:
        await message.answer("⛔ Не удалось найти пользователя в упоминании.")
        return

    current_user_role = get_user_role(user_id)
    if set_role(target_user_id, "cur", current_user_role):
        await message.answer(f"Вы назначили [id{target_user_id}|пользователя] куратором модерации.")
    else:
        await message.answer("⛔ У вас недостаточно прав для назначения этой роли.")

# Команда для снятия роли через упоминание
@bot.on.message(text="/user <mention>")
async def remove_owner_handler(message: Message, mention: str):
    user_id = message.from_id  # ID пользователя, который отправил команду
    target_user_id = await get_user_id_from_mention(message, mention)  # ID пользователя, которого упомянули

    if not target_user_id:
        await message.answer("⛔ Не удалось найти пользователя в упоминании.")
        return

    current_user_role = get_user_role(user_id)  # Получаем роль текущего пользователя
    if can_assign_role(current_user_role, "chief"):
        # Если текущий пользователь может снять роль
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET role = NULL WHERE user_id = ?", (target_user_id,))
        conn.commit()
        conn.close()

        await message.answer(f"Роль была снята с [id{target_user_id}|пользователя].")
    else:
        await message.answer("⛔ У вас недостаточно прав для снятия этой роли.")

# Команда "регистрация"
@bot.on.message(text="/reg")
async def register_handler(message: Message):
    user_id = message.from_id

    try:
        # Проверяем, существует ли пользователь в базе данных
        if add_user(user_id):  # Предполагается, что add_user возвращает True, если пользователь добавлен, и False, если он уже существует
            await message.reply("✅ Вы успешно зарегистрированы!")
        else:
            await message.reply("Вы уже зарегистрированы в системе.")
    except Exception as e:
        await message.reply(f"⛔ Произошла ошибка при регистрации: {e}")

# Команда для выдачи монет
@bot.on.message(text="выдать <mention> <amount:int>")
async def give_coins_handler(message: Message, mention: str, amount: int):
    if message.from_id not in ADMINS:
        await message.reply("⛔ У вас нет прав для использования этой команды.")
        return

    if amount <= 0:
        await message.reply("⛔ Сумма должна быть больше 0.")
        return

    user_id = await get_user_id_from_mention(message, mention)
    if not user_id:
        await message.reply("⛔ Не удалось определить пользователя.")
        return

    current_balance = get_balance(user_id)
    new_balance = current_balance + amount
    update_balance(user_id, new_balance)

    await message.reply(f"✅ Вы успешно выдали {amount} монет [id{user_id}|пользователю]. Новый баланс: {new_balance}.")

# Команда для отображения всех доступных команд
@bot.on.message(text="/cmd")
async def commands_handler(message: Message):
    commands_text = """
    📝 Список доступных команд:

    Команды участников:
    /руководство - показать список сотрудников и их роли.
    /reg - регистрация в системе.
    /balance - показать баланс пользователя.
    /shop - показать доступные товары в магазине.
    /buy - купить товар из магазина.
    /rr - играть в русскую рулетку.

    Команды заместителя главного модератора:
    /addcur - назначить пользователя куратором модерации.
    /user - снять роль с пользователя.

    Команды главного модератора:
    /обнулить - обнулить баланс пользователя.
    /addzgm - назначить пользователя заместителем главного модератора.
    /выдать - выдать коины пользователю.
    """
    await message.reply(commands_text)

# Команда "баланс"
@bot.on.message(text="/balance")
async def balance_handler(message: Message):
    user_id = message.from_id
    add_user(user_id)
    balance = get_balance(user_id)
    await message.reply(f"Ваш баланс: {balance} Moderation Coins.")

# Команда "магазин"
@bot.on.message(text="/shop")
async def shop_handler(message: Message):
    shop_text = "📜 Магазин:\n"
    for category, items in SHOP.items():
        shop_text += f"\n🔹 {category}\n"
        for item_id, item in items.items():
            shop_text += f"  {item_id}. {item['name']} — {item['price']} M-Coins\n"
    await message.reply(shop_text)

# Команда "купить"
@bot.on.message(text="/buy <item_id:int>")
async def buy_handler(message: Message, item_id: int):
    user_id = message.from_id
    add_user(user_id)

    item = None
    for category_items in SHOP.values():
        item = category_items.get(item_id)
        if item:
            break

    if not item:
        await message.reply("Такого товара нет в магазине!")
        return

    balance = get_balance(user_id)
    if balance < item["price"]:
        await message.reply("Недостаточно M-Coins для покупки.")
        return

    update_balance(user_id, -item["price"])
    await message.reply(f"Вы успешно купили {item['name']} за {item['price']} монет!")

# Команда "русская рулетка"
@bot.on.message(text="/rr")
async def russian_roulette_handler(message: Message):
    import random
    user_id = message.from_id
    add_user(user_id)

    balance = get_balance(user_id)
    if balance < 10:
        await message.reply("Недостаточно M-Coins для игры. Требуется минимум 10 монет.")
        return

    update_balance(user_id, -10)  # Снимаем 10 монет за участие
    if random.randint(1, 6) == 1:
        prize = 50
        update_balance(user_id, prize)
        await message.reply(f"💥 Бах! Вы победили и выиграли {prize} монет! Ваш новый баланс: {get_balance(user_id)} монет.")
    else:
        await message.reply(f"😌 Осечка. Вы проиграли 10 монет. Ваш новый баланс: {get_balance(user_id)} монет.")

# Команда "обнулить"
@bot.on.message(text="/обнулить <mention>")
async def reset_balance_handler(message: Message, mention: str):
    if message.from_id not in ADMINS:
        await message.reply("⛔ У вас нет прав для использования этой команды.")
        return

    user_id = await get_user_id_from_mention(message, mention)
    if not user_id:
        await message.reply("⛔ Не удалось определить пользователя. Проверьте правильность упоминания.")
        return

    try:
        # Обновление баланса пользователя на 0
        update_balance(user_id, -get_balance(user_id))  # Убираем все монеты с баланса
        await message.reply(f"✅ Баланс [id{user_id}|пользователя] был обнулен.")
    except Exception as e:
        await message.reply(f"⛔ Ошибка: {e}")

# Запуск бота
bot.run_forever()
