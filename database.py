import os
import sqlite3
from werkzeug.security import generate_password_hash


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

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
# POSTGRES DATABASE WRAPPER
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
    # RENDER POSTGRESQL
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
    # LOCAL SQLITE
    # =====================================================

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

def create_tables(conn, database_url):

    cursor = conn.cursor()

    # =====================================================
    # POSTGRESQL TABLES
    # =====================================================

    if database_url:

        # USERS
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

        # COURSES
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                level TEXT DEFAULT 'Beginner',
                duration TEXT DEFAULT '4 Weeks'
            )
        """)

        # QUIZ RESULTS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                course_id INTEGER,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)
                    REFERENCES users(id),
                FOREIGN KEY (course_id)
                    REFERENCES courses(id)
            )
        """)

        # ONLINE QUESTIONS
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

        # LESSON PROGRESS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lesson_progress (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                lesson_number INTEGER NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, course_id, lesson_number),
                FOREIGN KEY(user_id)
                    REFERENCES users(id)
            )
        """)

        # CERTIFICATES
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS certificates (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                certificate_code TEXT UNIQUE NOT NULL,
                issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, course_id),
                FOREIGN KEY(user_id)
                    REFERENCES users(id)
            )
        """)

    # =====================================================
    # SQLITE TABLES
    # =====================================================

    else:

        # USERS
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

        # COURSES
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                level TEXT DEFAULT 'Beginner',
                duration TEXT DEFAULT '4 Weeks'
            )
        """)

        # QUIZ RESULTS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id INTEGER,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)
                    REFERENCES users(id),
                FOREIGN KEY (course_id)
                    REFERENCES courses(id)
            )
        """)

        # ONLINE QUESTIONS
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

        # LESSON PROGRESS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lesson_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                lesson_number INTEGER NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, course_id, lesson_number),
                FOREIGN KEY(user_id)
                    REFERENCES users(id)
            )
        """)

        # CERTIFICATES
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS certificates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                certificate_code TEXT UNIQUE NOT NULL,
                issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, course_id),
                FOREIGN KEY(user_id)
                    REFERENCES users(id)
            )
        """)

    conn.commit()


# =========================================================
# DEFAULT COURSES
# =========================================================

DEFAULT_COURSES = [

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


# =========================================================
# INSERT DEFAULT ADMIN
# =========================================================

def create_default_admin(conn):

    cursor = conn.cursor()

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

        print("Default admin created.")


# =========================================================
# INSERT DEFAULT COURSES
# =========================================================

def create_default_courses(conn):

    cursor = conn.cursor()

    course_count = cursor.execute(
        "SELECT COUNT(*) AS count FROM courses"
    ).fetchone()["count"]

    if course_count == 0:

        cursor.executemany("""
            INSERT INTO courses
            (title, description, level, duration)
            VALUES (?, ?, ?, ?)
        """, DEFAULT_COURSES)

        print("Default courses created.")

    conn.commit()


# =========================================================
# MIGRATE COURSES FROM SQLITE
# =========================================================

def migrate_courses_from_sqlite(conn):

    if not os.path.exists(DATABASE):

        print("Local SQLite database not found.")
        return {}

    try:

        sqlite_conn = sqlite3.connect(DATABASE)

        sqlite_conn.row_factory = sqlite3.Row

        sqlite_cursor = sqlite_conn.cursor()

        # Check courses table
        sqlite_cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            AND name='courses'
        """)

        if not sqlite_cursor.fetchone():

            sqlite_conn.close()

            print("SQLite courses table not found.")

            return {}

        sqlite_courses = sqlite_cursor.execute("""
            SELECT
                id,
                title,
                description,
                level,
                duration
            FROM courses
            ORDER BY id
        """).fetchall()

        postgres_cursor = conn.cursor()

        course_map = {}

        for course in sqlite_courses:

            existing = postgres_cursor.execute(
                """
                SELECT id
                FROM courses
                WHERE title = ?
                """,
                (course["title"],)
            ).fetchone()

            if existing:

                course_map[course["id"]] = existing["id"]

            else:

                postgres_cursor.execute("""
                    INSERT INTO courses
                    (title, description, level, duration)
                    VALUES (?, ?, ?, ?)
                    RETURNING id
                """, (
                    course["title"],
                    course["description"],
                    course["level"],
                    course["duration"]
                ))

                new_course = postgres_cursor.fetchone()

                course_map[course["id"]] = new_course["id"]

        conn.commit()

        sqlite_conn.close()

        print(
            "SQLite courses migrated:",
            len(course_map)
        )

        return course_map

    except Exception as e:

        print(
            "Course migration error:",
            str(e)
        )

        return {}


# =========================================================
# MIGRATE QUESTIONS FROM SQLITE TO POSTGRESQL
# =========================================================

def migrate_questions_from_sqlite(conn, course_map):

    # -----------------------------------------------------
    # SQLite database must exist in project
    # -----------------------------------------------------

    if not os.path.exists(DATABASE):

        print(
            "computer_education.db not found."
        )

        print(
            "Questions were NOT migrated."
        )

        return

    try:

        # =================================================
        # OPEN SQLITE
        # =================================================

        sqlite_conn = sqlite3.connect(DATABASE)

        sqlite_conn.row_factory = sqlite3.Row

        sqlite_cursor = sqlite_conn.cursor()

        # =================================================
        # CHECK TABLE
        # =================================================

        sqlite_cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            AND name='online_questions'
        """)

        table = sqlite_cursor.fetchone()

        if not table:

            print(
                "SQLite online_questions table not found."
            )

            sqlite_conn.close()

            return

        # =================================================
        # COUNT SQLITE QUESTIONS
        # =================================================

        sqlite_count = sqlite_cursor.execute("""
            SELECT COUNT(*)
            FROM online_questions
        """).fetchone()[0]

        print(
            "SQLite questions found:",
            sqlite_count
        )

        if sqlite_count == 0:

            print(
                "SQLite database contains 0 questions."
            )

            sqlite_conn.close()

            return

        # =================================================
        # COUNT POSTGRES QUESTIONS
        # =================================================

        postgres_cursor = conn.cursor()

        postgres_count = postgres_cursor.execute("""
            SELECT COUNT(*)
            FROM online_questions
        """).fetchone()["count"]

        print(
            "PostgreSQL questions before migration:",
            postgres_count
        )

        # =================================================
        # IMPORTANT
        # Do not duplicate questions
        # =================================================

        if postgres_count > 0:

            print(
                "PostgreSQL already contains questions."
            )

            print(
                "Migration skipped to prevent duplicates."
            )

            sqlite_conn.close()

            return

        # =================================================
        # READ QUESTIONS
        # =================================================

        questions = sqlite_cursor.execute("""
            SELECT
                subject,
                question,
                option_a,
                option_b,
                option_c,
                option_d,
                correct_answer,
                difficulty,
                source,
                category,
                course_id
            FROM online_questions
            ORDER BY id
        """).fetchall()

        # =================================================
        # INSERT QUESTIONS
        # =================================================

        insert_sql = """
            INSERT INTO online_questions
            (
                subject,
                question,
                option_a,
                option_b,
                option_c,
                option_d,
                correct_answer,
                difficulty,
                source,
                category,
                course_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        migrated = 0

        batch = []

        for q in questions:

            old_course_id = q["course_id"]

            new_course_id = None

            if old_course_id is not None:

                new_course_id = course_map.get(
                    old_course_id
                )

            batch.append((
                q["subject"],
                q["question"],
                q["option_a"],
                q["option_b"],
                q["option_c"],
                q["option_d"],
                q["correct_answer"],
                q["difficulty"],
                q["source"],
                q["category"],
                new_course_id
            ))

        # =================================================
        # BULK INSERT
        # =================================================

        if batch:

            postgres_cursor.executemany(
                insert_sql,
                batch
            )

            migrated = len(batch)

        conn.commit()

        # =================================================
        # VERIFY
        # =================================================

        final_count = postgres_cursor.execute("""
            SELECT COUNT(*)
            FROM online_questions
        """).fetchone()["count"]

        print(
            "Questions migrated:",
            migrated
        )

        print(
            "PostgreSQL questions after migration:",
            final_count
        )

        sqlite_conn.close()

    except Exception as e:

        conn.rollback()

        print(
            "QUESTION MIGRATION ERROR:"
        )

        print(
            str(e)
        )

        raise


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def init_db():

    database_url = os.getenv("DATABASE_URL")

    conn = get_db()

    try:

        # =================================================
        # CREATE TABLES
        # =================================================

        create_tables(
            conn,
            database_url
        )

        # =================================================
        # ADMIN
        # =================================================

        create_default_admin(conn)

        conn.commit()

        # =================================================
        # RENDER POSTGRESQL
        # =================================================

        if database_url:

            print("")
            print("==============================")
            print("RENDER POSTGRESQL DETECTED")
            print("==============================")

            # -------------------------------------------------
            # Make sure default courses exist first
            # -------------------------------------------------

            create_default_courses(conn)

            # -------------------------------------------------
            # Migrate courses from local SQLite
            # -------------------------------------------------

            course_map = migrate_courses_from_sqlite(
                conn
            )

            # -------------------------------------------------
            # Migrate questions
            # -------------------------------------------------

            migrate_questions_from_sqlite(
                conn,
                course_map
            )

        # =================================================
        # LOCAL SQLITE
        # =================================================

        else:

            print("")
            print("==============================")
            print("LOCAL SQLITE DATABASE")
            print("==============================")

            create_default_courses(conn)

    except Exception as e:

        conn.rollback()

        print("")
        print("==============================")
        print("DATABASE ERROR")
        print("==============================")

        print(str(e))

        raise

    finally:

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

    if database_url:

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lesson_progress (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                lesson_number INTEGER NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, course_id, lesson_number),
                FOREIGN KEY(user_id)
                    REFERENCES users(id)
            )
        """)

    else:

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lesson_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                lesson_number INTEGER NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, course_id, lesson_number),
                FOREIGN KEY(user_id)
                    REFERENCES users(id)
            )
        """)

    conn.commit()

    conn.close()


# =========================================================
# RUN DIRECTLY
# =========================================================

if __name__ == "__main__":

    initialize_database()

    print("")
    print("==============================")
    print("DATABASE INITIALIZED")
    print("==============================")