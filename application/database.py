import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

class Database:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'database', 'drone_monitor.db')
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def has_admin(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def create_user(self, username, password):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            password_hash = generate_password_hash(password)
            cursor.execute(
                'INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, 1)',
                (username, password_hash)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def verify_user(self, username, password):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()
        if result:
            user_id, password_hash = result
            if check_password_hash(password_hash, password):
                return user_id
        return None

    def get_user(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, is_admin FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return {'id': result[0], 'username': result[1], 'is_admin': bool(result[2])}
        return None