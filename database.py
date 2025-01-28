import sqlite3
from datetime import datetime

def get_db_connection():
    """Подключение к базе данных."""
    conn = sqlite3.connect("database.db")  # Укажите правильный путь к вашей базе данных
    conn.row_factory = sqlite3.Row  # Это позволяет работать с результатами как с объектами
    return conn

def add_user(user_id):
    """Добавить пользователя в базу данных."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def get_balance(user_id):
    """Получить баланс пользователя."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def update_balance(user_id, amount):
    """Обновить баланс пользователя."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()
