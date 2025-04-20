# init_db.py
import sqlite3
import os

if not os.path.exists("db"):
    os.makedirs("db")

with open("schema.sql", "r") as f:
    schema = f.read()

conn = sqlite3.connect("db/database.db")
conn.executescript(schema)
conn.commit()
conn.close()

print("🎉 Database initialized successfully.")
