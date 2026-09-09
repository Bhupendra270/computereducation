import os
import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = "computer_education.db"


# =========================================================
# POSTGRES CURSOR
# =========================================================

class PostgresCursor:
    def __init__(self, cursor):
        self.cursor = cursor

    def _convert_query(self, query):
        return query.replace("?", "%s")

    def execute(self, query, params=None):
        query = self._convert_query(query)

        if params is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, params)

        return self

    def executemany(self, query, params):
        query = self._convert_query(query)
        self.cursor.executemany(query, params)
        return self

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def __iter__(self):
        return iter(self.cursor)

    @property
    def rowcount(self):
        return self.cursor.rowcount


# =========================================================
# POSTGRES DATABASE
# =========================================================

class PostgresDB:
    def __init__(self, connection):
        self.connection = connection

    def cursor(self):
        return PostgresCursor(
            self.connection.cursor()
        )

    def execute(self, query, params=None):
        cursor = self.cursor()
        cursor.execute(query, params)
        return cursor

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        self.connection.close()


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():

    database_url = os.getenv("DATABASE_URL")

    # =====================================================
    # RENDER / POSTGRESQL
    # =====================================================

    if database_url:

        import psycopg2
        from psycopg2.extras import RealDictCursor

        connection = psycopg2.connect(
            database_url,
            cursor_factory=RealDictCursor
        )

        return PostgresDB(connection)

    # =====================================================
    # LOCAL / SQLITE
    # =====================================================

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    return conn


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def init_db():

    database_url = os.getenv("DATABASE_URL")

    conn = get_db()
    cursor = conn.cursor()

    # =====================================================
    # POSTGRESQL
    # =====================================================

    if database_url:

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'student',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                level TEXT DEFAULT 'Beginner',
                duration TEXT DEFAULT '4 Weeks'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                course_id INTEGER,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS online_questions (
                id SERIAL PRIMARY KEY,
                subject TEXT,
                question TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                difficulty TEXT DEFAULT 'Easy',
                source TEXT,
                category TEXT,
                course_id INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lesson_progress (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                lesson_number INTEGER NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, course_id, lesson_number),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS certificates (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                certificate_code TEXT UNIQUE NOT NULL,
                issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, course_id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

    # =====================================================
    # SQLITE
    # =====================================================

    else:

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'student',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                level TEXT DEFAULT 'Beginner',
                duration TEXT DEFAULT '4 Weeks'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id INTEGER,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS online_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT,
                question TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                difficulty TEXT DEFAULT 'Easy',
                source TEXT,
                category TEXT,
                course_id INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lesson_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                lesson_number INTEGER NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, course_id, lesson_number),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS certificates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                certificate_code TEXT UNIQUE NOT NULL,
                issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, course_id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

    # =====================================================
    # DEFAULT ADMIN
    # =====================================================

    admin = cursor.execute(
        "SELECT id FROM users WHERE email = ?",
        ("admin@example.com",)
    ).fetchone()

    if not admin:

        cursor.execute("""
            INSERT INTO users
            (name, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (
            "Administrator",
            "admin@example.com",
            generate_password_hash("admin123"),
            "admin"
        ))

    # =====================================================
    # DEFAULT COURSES
    # =====================================================

    course_count = cursor.execute(
        "SELECT COUNT(*) AS count FROM courses"
    ).fetchone()["count"]

    if course_count == 0:

        courses = [
            (
                "Computer Fundamentals",
                "Learn the basics of computers, hardware and software.",
                "Beginner",
                "4 Weeks"
            ),
            (
                "MS Office",
                "Learn Word, Excel and PowerPoint.",
                "Beginner",
                "6 Weeks"
            ),
            (
                "Internet & Email",
                "Learn internet browsing, email and online safety.",
                "Beginner",
                "3 Weeks"
            ),
            (
                "Python Programming",
                "Learn Python programming from basics.",
                "Intermediate",
                "8 Weeks"
            ),
            (
                "Web Development",
                "Learn HTML, CSS, JavaScript and Flask.",
                "Intermediate",
                "10 Weeks"
            )
        ]

        cursor.executemany("""
            INSERT INTO courses
            (title, description, level, duration)
            VALUES (?, ?, ?, ?)
        """, courses)

    conn.commit()
    conn.close()


# =========================================================
# INITIALIZE ALL DATABASE TABLES
# =========================================================

def initialize_database():
    init_db()


# =========================================================
# PROGRESS TABLE
# =========================================================

def init_progress_table():

    database_url = os.getenv("DATABASE_URL")

    conn = get_db()
    cursor = conn.cursor()

    # =====================================================
    # POSTGRESQL
    # =====================================================

    if database_url:

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lesson_progress (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                lesson_number INTEGER NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, course_id, lesson_number),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

    # =====================================================
    # SQLITE
    # =====================================================

    else:

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lesson_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                lesson_number INTEGER NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, course_id, lesson_number),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

    conn.commit()
    conn.close()


# =========================================================
# RUN DIRECTLY
# =========================================================

if __name__ == "__main__":

    initialize_database()

    print("Database initialized successfully!")