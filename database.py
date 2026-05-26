import sqlite3

DB_NAME = 'timesheet.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    # Включаем поддержку внешних ключей
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        role TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS projects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS time_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        project_id INTEGER,
                        start_time TEXT,
                        end_time TEXT,
                        duration_seconds INTEGER,
                        description TEXT,
                        status TEXT DEFAULT 'На рассмотрении',
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                        FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE)''')

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (name, role) VALUES ('Иван Иванов', 'Сотрудник')")
        cursor.execute("INSERT INTO users (name, role) VALUES ('Анна Смирнова', 'Руководитель')")
        cursor.execute("INSERT INTO projects (name) VALUES ('Разработка CRM')")
        cursor.execute("INSERT INTO projects (name) VALUES ('Обновление сайта')")

    conn.commit()
    conn.close()

# --- ФУНКЦИИ ДЛЯ РАБОТЫ СО ВРЕМЕНЕМ ---
def get_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def get_projects():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM projects")
    projects = cursor.fetchall()
    conn.close()
    return projects

def save_time_entry(user_id, project_id, start_time, end_time, duration, description):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO time_entries (user_id, project_id, start_time, end_time, duration_seconds, description)
                      VALUES (?, ?, ?, ?, ?, ?)''', (user_id, project_id, start_time, end_time, duration, description))
    conn.commit()
    conn.close()

def get_pending_entries():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''SELECT te.id, u.name, p.name, te.start_time, te.duration_seconds, te.description 
                      FROM time_entries te JOIN users u ON te.user_id = u.id JOIN projects p ON te.project_id = p.id
                      WHERE te.status = 'На рассмотрении' ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_entry_status(entry_id, new_status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE time_entries SET status = ? WHERE id = ?", (new_status, entry_id))
    conn.commit()
    conn.close()

def get_approved_report():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''SELECT u.name, p.name, SUM(te.duration_seconds) FROM time_entries te
                      JOIN users u ON te.user_id = u.id JOIN projects p ON te.project_id = p.id
                      WHERE te.status = 'Утверждено' GROUP BY u.name, p.name''')
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- НОВЫЕ ФУНКЦИИ УПРАВЛЕНИЯ (CRUD) ---
def add_user(name, role="Сотрудник"):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("INSERT INTO users (name, role) VALUES (?, ?)", (name, role))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def add_project(name):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("INSERT INTO projects (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def edit_project(project_id, new_name):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("UPDATE projects SET name = ? WHERE id = ?", (new_name, project_id))
    conn.commit()
    conn.close()

def delete_project(project_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
