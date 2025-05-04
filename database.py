import sqlite3
from datetime import datetime

DB_NAME = 'medistics.db'

def get_db_connection():
    """Open a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database tables, updating schema if needed."""
    conn = get_db_connection()
    cur = conn.cursor()
    # Users table – ensure plain password column
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    table_exists = cur.fetchone()
    if table_exists:
        # If users table exists, check for old password_hash column
        cur.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cur.fetchall()]
        if 'password_hash' in columns:
            try:
                # Rename old password_hash column to password
                cur.execute("ALTER TABLE users RENAME COLUMN password_hash TO password")
            except sqlite3.OperationalError:
                # If ALTER not supported, drop and recreate users (and dependent tables)
                cur.execute("DROP TABLE IF EXISTS issues")
                cur.execute("DROP TABLE IF EXISTS payments")
                cur.execute("DROP TABLE IF EXISTS users")
    # Create users table with plain password (if not exists or after drop)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            username TEXT UNIQUE,
            province TEXT,
            referral_source TEXT,
            theme TEXT,
            subscription_plan TEXT,
            signup_date TEXT,
            bio_correct INTEGER DEFAULT 0,
            bio_total INTEGER DEFAULT 0,
            chem_correct INTEGER DEFAULT 0,
            chem_total INTEGER DEFAULT 0,
            phy_correct INTEGER DEFAULT 0,
            phy_total INTEGER DEFAULT 0,
            eng_correct INTEGER DEFAULT 0,
            eng_total INTEGER DEFAULT 0,
            lr_correct INTEGER DEFAULT 0,
            lr_total INTEGER DEFAULT 0,
            openai_api_key TEXT
        );
    """)
    # Questions table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            question_text TEXT,
            option1 TEXT,
            option2 TEXT,
            option3 TEXT,
            option4 TEXT,
            correct_option INTEGER,
            explanation TEXT
        );
    """)
    # Issues (support tickets) table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT,
            description TEXT,
            report_date TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    # Payments table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            plan TEXT,
            amount REAL,
            method TEXT,
            payment_date TEXT,
            status TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    conn.close()
