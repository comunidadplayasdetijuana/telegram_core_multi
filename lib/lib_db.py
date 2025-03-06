import sqlite3
from datetime import datetime

db_file = "./db/dbApp.db"

def init_db():
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER,
            username TEXT,
            nickname TEXT,
            first_name TEXT,
            last_name TEXT,
            contact_userid INTEGER,
            phone TEXT,
            notifications_enabled INTEGER DEFAULT 1
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
            date TEXT,
            user_id INTEGER,
            username TEXT,
            nickname TEXT,
            first_name TEXT,
            last_name TEXT,
            action TEXT,
            note TEXT
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS credits (
            date TEXT,
            user_id INTEGER,
            username TEXT,
            nickname TEXT,
            first_name TEXT,
            last_name TEXT,
            credits INTEGER,
            note TEXT
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_actions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            action_type TEXT,  -- 'ban' o 'temporary_ban'
            reason TEXT,
            start_date TEXT,
            end_date TEXT,  -- Solo para 'temporary_ban'
            status TEXT,  -- 'active' o 'inactive'
            note TEXT
        )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS referral_codes (
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER NOT NULL,
                code TEXT NOT NULL
            )
        ''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS help_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            problem TEXT,
            response TEXT,
            response_sent INTEGER DEFAULT 0,
            date_requested DATETIME DEFAULT CURRENT_TIMESTAMP,
            date_responded DATETIME
        )''')



def get_user_data(user_id):

    print(f"getting data({user_id})")
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username, nickname, first_name, last_name FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        
    if result:
        user_id, username, nickname, first_name, last_name = result
        return user_id, username, nickname, first_name, last_name
    else:
        return None  

def register_user(user_id, username, nickname, first_name, last_name, contact_userid=None, phone=None, notifications_enabled=1):
    date = datetime.now().strftime("%Y%m%d %I:%M %p")
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO users (user_id, username, nickname, first_name, last_name, contact_userid, phone, notifications_enabled)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                       (user_id, username, nickname, first_name, last_name, contact_userid, phone, notifications_enabled))

def get_user_config(user_id):
    """Obtiene las configuraciones del usuario desde la base de datos."""
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            # Convertimos la fila en un diccionario para facilitar el acceso
            user_settings = {
                "user_id": row[0],
                "username": row[1],
                "nickname": row[2],
                "first_name": row[3],
                "last_name": row[4],
                "contact_userid": row[5],
                "phone": row[6],
                "notifications_enabled": row[7]
            }
            return user_settings
        return None


def update_user_config(user_id, key, value):
    """Actualiza una configuración del usuario en la base de datos."""
    if key not in ["nickname", "first_name", "last_name", "contact_userid", "phone", "notifications_enabled"]:
        raise ValueError("Parámetro no válido para configuración.")

    # Modificamos la configuración en la base de datos
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET {key} = ? WHERE user_id = ?", (value, user_id))
        conn.commit()


def log_user_action(user_id, action_type, reason, start_date, end_date=None, status="active", note=None):
    date = datetime.now().strftime("%Y%m%d %I:%M %p")
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_actions (user_id, action_type, reason, start_date, end_date, status, note) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                       (user_id, action_type, reason, start_date, end_date, status, note))
        
def deactivate_user_action(user_id, action_id):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE user_actions SET status = ? WHERE id = ? AND user_id = ?", 
                       ("inactive", action_id, user_id))


def log_action(user_id, action, note=None):
    
    date = datetime.now().strftime("%Y%m%d %I:%M %p")
    user_data = get_user_data(user_id)  # Debe ser una función que obtenga los datos del usuario desde la BD

    #print("log acction", user_data)

    if not user_data:
        print(f"Error: Usuario {user_id} no encontrado en la base de datos.")
        return

    userid, username, nickname, first_name, last_name = user_data  # Ajusta según la estructura de la BD

    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logs VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                       (date, user_id, username, nickname, first_name, last_name, action, note))


def add_credit(user_id, amount, note):

    user_data = get_user_data(user_id)

    print(user_data)
    
    if user_data:
        user_id, username, nickname, first_name, last_name = user_data
        date = datetime.now().strftime("%Y%m%d %I:%M %p")
        
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO credits VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                           (date, user_id, username, nickname, first_name, last_name, amount, note))
    else:
        raise ValueError("User not found.")


def check_credits(user_id):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(credits) FROM credits WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0

def remove_last_credit(user_id):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT rowid, date, credits FROM credits WHERE user_id = ? ORDER BY rowid DESC LIMIT 1", (user_id,))
        last_entry = cursor.fetchone()
        if last_entry:
            cursor.execute("DELETE FROM credits WHERE rowid = ?", (last_entry[0],))
            return last_entry[1], last_entry[2]  # Retorna la fecha y la cantidad eliminada
        return None, None


def insert_referral_code(user_id, code):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO referral_codes (created_by, code)
            VALUES (?, ?)
        ''', (user_id, code))
        conn.commit()
    
    return code



init_db()