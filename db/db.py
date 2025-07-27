import sqlite3
import os

DB_PATH = "lista.db"

def init_db():
    if not os.path.exists(DB_PATH):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE lista (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item TEXT NOT NULL,
                    quantidade INTEGER NOT NULL
                );
            """)
            
        print("Banco de dados criado.")
    else:
        print("Banco já existe.")

def executar_comando(query: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        if query.strip().lower().startswith("select"):
            return cursor.fetchall()
        else:
            conn.commit()
            return None

def listar_itens():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT item, quantidade FROM lista")
        return cursor.fetchall()