import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = "computer_education.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # =========================================================
    # USERS
    # =========================================================
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

    # =========================================================
    # COURSES
    # =========================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            level TEXT DEFAULT 'Beginner',
            duration TEXT DEFAULT '4 Weeks'
        )
    """)

    # =========================================================
    # QUIZ RESULTS
    # =========================================================
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

    # =========================================================
    # ONLINE QUIZ QUESTIONS
    # =========================================================
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

    # =========================================================
    # LESSON PROGRESS
    # =========================================================
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

    # =========================================================
    # CERTIFICATES
    # =========================================================
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

    # =========================================================
    # DEFAULT ADMIN
    # =========================================================
    admin = cursor.execute(
        "SELECT id FROM users WHERE email = ?",
        ("admin@example.com",)
    ).fetchone()

    if not admin:
        cursor.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (
            "Administrator",
            "admin@example.com",
            generate_password_hash("admin123"),
            "admin"
        ))

    # =========================================================
    # DEFAULT COURSES
    # =========================================================
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
# RUN DIRECTLY
# =========================================================

if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully!")
def init_progress_table():
    conn = get_db()
    cursor = conn.cursor()

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

