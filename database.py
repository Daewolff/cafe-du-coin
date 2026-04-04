import sqlite3
import os

# Chemin ABSOLU vers la base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "database.db")

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS commandes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            produit TEXT NOT NULL,
            quantite INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("Base de données initialisée avec succès.")
