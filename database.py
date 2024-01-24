import sqlite3

conn = sqlite3.connect('database.db')

conn.execute('''CREATE TABLE products
                (productId INTEGER PRIMARY KEY,
                name TEXT,
                price REAL,
                image TEXT,
                stock INTEGER
                )''')