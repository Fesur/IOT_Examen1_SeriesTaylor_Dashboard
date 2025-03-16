import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_name="series_math.db"):
        self.db_name = db_name
        self.conn = None
        self.init_db()
        
    def init_db(self):
        """Inicializa la base de datos con las tablas necesarias."""
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        )
        ''')
        
        # Tabla para los cálculos de series
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            series_type TEXT NOT NULL,  -- 'sin', 'cos', 'tan'
            x_value REAL NOT NULL,
            n_terms INTEGER NOT NULL,
            result REAL NOT NULL,
            exact_value REAL NOT NULL,
            error REAL NOT NULL,
            calculation_time TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        self.conn.commit()
    
    def add_user(self, username):
        """Añade un nuevo usuario a la base de datos."""
        try:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute("INSERT INTO users (username, created_at) VALUES (?, ?)", 
                           (username, now))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # El usuario ya existe, obtenemos su ID
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            return cursor.fetchone()[0]
    
    def save_calculation(self, user_id, series_type, x_value, n_terms, result, exact_value, error):
        """Guarda un cálculo en la base de datos."""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO calculations 
            (user_id, series_type, x_value, n_terms, result, exact_value, error, calculation_time) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, series_type, x_value, n_terms, result, exact_value, error, now))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_user_calculations(self, user_id):
        """Obtiene todos los cálculos realizados por un usuario."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT series_type, x_value, n_terms, result, exact_value, error, calculation_time 
            FROM calculations 
            WHERE user_id = ? 
            ORDER BY calculation_time DESC
            ''', (user_id,))
        return cursor.fetchall()
    
    def get_all_calculations(self):
        """Obtiene todos los cálculos de la base de datos junto con el nombre de usuario."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT u.username, c.series_type, c.x_value, c.n_terms, c.result, c.exact_value, c.error, c.calculation_time 
            FROM calculations c
            JOIN users u ON c.user_id = u.id
            ORDER BY c.calculation_time DESC
            ''')
        return cursor.fetchall()
    
    def close(self):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()
