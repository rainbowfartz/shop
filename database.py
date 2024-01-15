import sqlite3

conn = sqlite3.connect('database.db')

conn.execute('''CREATE TABLE products
                (productId INTEGER PRIMARY KEY,
                name TEXT,
                price REAL,
                image TEXT,
                stock INTEGER
                )''')

conn.execute('''CREATE TABLE users 
		(userId INTEGER PRIMARY KEY, 
		password TEXT,
		email TEXT,
		firstName TEXT,
		lastName TEXT,
		address1 TEXT,
		address2 TEXT,
		zipcode TEXT,
		city TEXT,
		state TEXT,
		country TEXT,
		phone TEXT
		)''')

conn.close()