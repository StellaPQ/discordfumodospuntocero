import requests
import sqlite3

def get_duck_image_url():    
    url = 'https://random-d.uk/api/random'
    res = requests.get(url)
    data = res.json()
    return data['url']

def setup_db():
    with sqlite3.connect("economy.db") as db:
        cursor = db.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance INTEGER, bank INTEGER)")
        db.commit()

def update_balance(user_id, amount, in_bank=False):
    with sqlite3.connect("economy.db") as db:
        cursor = db.cursor()
        column = "bank" if in_bank else "balance"
        cursor.execute(f"UPDATE users SET {column} = {column} + ? WHERE id=?", (amount, user_id))
        db.commit()

def get_top_users():
    with sqlite3.connect("economy.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT id, balance FROM users ORDER BY balance DESC LIMIT 10")
        return cursor.fetchall()