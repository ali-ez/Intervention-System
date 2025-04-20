import sqlite3

conn = sqlite3.connect('db/database.db')
cursor = conn.cursor()

cursor.execute('SELECT * FROM locations')
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
