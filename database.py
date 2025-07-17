import sqlite3

DB_NAME = "jobs.db"

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )''')
    # Job Applications Table
    c.execute('''CREATE TABLE IF NOT EXISTS job_applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        company TEXT,
        position TEXT,
        status TEXT,
        date_applied TEXT,
        deadline TEXT,
        resume TEXT,
        cover_letter TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    conn.commit()
    conn.close()

def register_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Check if email already exists
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    if c.fetchone():
        conn.close()
        return False  # Already exists
    
    # Otherwise insert new user
    c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
    conn.commit()
    conn.close()
    return True


def authenticate_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    user = c.fetchone()
    conn.close()
    if user:
        return {"id": user[0], "email": user[1]}
    return None

def add_job(user_id, company, position, status, date_applied, deadline, resume_path, cover_letter_path):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO job_applications
        (user_id, company, position, status, date_applied, deadline, resume, cover_letter)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, company, position, status, date_applied, deadline, resume_path, cover_letter_path))
    conn.commit()
    conn.close()

def view_jobs(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM job_applications WHERE user_id = ?", (user_id,))
    data = c.fetchall()
    conn.close()
    return data

def update_job(job_id, company, position, status, date_applied, deadline):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        UPDATE job_applications 
        SET company = ?, position = ?, status = ?, date_applied = ?, deadline = ? 
        WHERE id = ?
    """, (company, position, status, date_applied, deadline, job_id))
    conn.commit()
    conn.close()

def update_job_status(job_id, new_status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE job_applications SET status = ? WHERE id = ?", (new_status, job_id))
    conn.commit()
    conn.close()

def delete_job(job_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM job_applications WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()
