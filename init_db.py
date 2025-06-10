import sqlite3
import os

def init_db():
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Create pets table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category_id INTEGER,
            photoUrls TEXT,
            status TEXT
        )
    ''')

    # Create categories table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    ''')

    # Create tags table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    ''')

    # Create pet_tags junction table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pet_tags (
            pet_id INTEGER,
            tag_id INTEGER,
            FOREIGN KEY (pet_id) REFERENCES pets(id),
            FOREIGN KEY (tag_id) REFERENCES tags(id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully")