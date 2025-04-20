import sqlite3

# الاتصال بقاعدة البيانات
conn = sqlite3.connect('db/database.db')
cursor = conn.cursor()

# بيانات المدرسة اللي هتدخلها
school_name = "Modern Academy"
city = "Cairo"
address = "45 Nasr Street"

# أمر الإدخال
cursor.execute('''
    INSERT INTO locations (school_name, city, address)
    VALUES (?, ?, ?)
''', (school_name, city, address))

conn.commit()
conn.close()

print("🏫 School inserted successfully.")
