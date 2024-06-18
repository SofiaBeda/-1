import sqlite3

def create_table():
    conn = sqlite3.connect('chat_app.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_table()
    print("Database setup completed.")