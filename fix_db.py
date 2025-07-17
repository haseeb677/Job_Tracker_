import sqlite3

conn = sqlite3.connect("jobs.db")
c = conn.cursor()

# Forcefully drop the broken users table
c.execute("DROP TABLE IF EXISTS users")

# Recreate tables properly
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)''')

print("✅ Dropped and recreated users table with email column.")

conn.commit()
conn.close()
