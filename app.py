from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database import get_db, init_db, init_progress_table

import json
import os


app = Flask(__name__)

app.secret_key = "computer-education-secret-key"

init_db()
init_progress_table()


# =========================================================
# HELPERS
# =========================================================

def is_logged_in():
    return "user_id" in session


def is_admin():
    return session.get("role") == "admin"


def load_questions():
    try:
        db = get_db()

        rows = db.execute("""
            SELECT
                id,
                subject,
                question,
                option_a,
                option_b,
                option_c,
                option_d,
                correct_answer,
                difficulty,
                source,
                category
            FROM online_questions
            ORDER BY id
        """).fetchall()

        questions = []

        subject_course = {
            "Computer Fundamentals": 1,
            "MS Office": 2,
            "Python Programming": 3,
            "Web Development": 4
        }

        for row in rows:
            questions.append({
                "id": row["id"],
                "subject": row["subject"],
                "course_id": subject_course.get(row["subject"]),
                "question": row["question"],
                "options": [
                    row["option_a"],
                    row["option_b"],
                    row["option_c"],
                    row["option_d"]
                ],
                "answer": row["correct_answer"],
                "difficulty": row["difficulty"],
                "source": row["source"],
                "category": row["category"]
            })

        print("DATABASE QUESTIONS LOADED:", len(questions))
        return questions

    except Exception as e:
        print("QUESTION LOAD ERROR:", e)
        return []


    # Main questions file: 5000 questions
    file_path = r"E:\html\questions_100.json"

    if not os.path.exists(file_path):
        return []

    with open(
        file_path,
        "r",
        encoding="utf-8-sig"
    ) as file:

        data = json.load(file)

    # Safety: हमेशा valid list return करें
    if not isinstance(data, list):
        return []

    return data


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        if not name or not email or not password:

            flash(
                "Please fill all fields.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        if len(password) < 6:

            flash(
                "Password must contain at least 6 characters.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        db = get_db()

        user = db.execute(
            """
            SELECT id
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if user:

            db.close()

            flash(
                "Email already registered.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        hashed_password = generate_password_hash(
            password
        )

        db.execute(
            """
            INSERT INTO users
            (name, email, password, role)
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                email,
                hashed_password,
                "student"
            )
        )

        db.commit()
        db.close()

        flash(
            "Account created successfully!",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        db = get_db()

        user = db.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        db.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["email"] = user["email"]
            session["role"] = user["role"]

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Invalid email or password.",
            "danger"
        )

    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("index")
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if not is_logged_in():
        return redirect(url_for("login"))

    db = get_db()

    total_users = db.execute(
        "SELECT COUNT(*) AS count FROM users"
    ).fetchone()["count"]

    total_courses = len(COURSES)
    total_questions = len(load_questions())

    user_id = session.get("user_id")

    completed_quizzes = db.execute(
        """
        SELECT COUNT(*) AS count
        FROM quiz_results
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()["count"]

    quiz_stats = db.execute(
        """
        SELECT
            COALESCE(
                ROUND(
                    AVG(
                        CASE
                            WHEN total > 0
                            THEN score * 100.0 / total
                        END
                    ),
                    1
                ),
                0
            ) AS average_score,

            COALESCE(
                MAX(
                    CASE
                        WHEN total > 0
                        THEN score * 100.0 / total
                    END
                ),
                0
            ) AS best_score

        FROM quiz_results
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()

    recent_quizzes = db.execute(
        """
        SELECT
            qr.score,
            qr.total,
            qr.created_at,
            c.title AS course_title
        FROM quiz_results qr
        LEFT JOIN courses c
            ON qr.course_id = c.id
        WHERE qr.user_id = ?
        ORDER BY qr.id DESC
        LIMIT 5
        """,
        (user_id,)
    ).fetchall()

    # =========================================================
    # LESSON PROGRESS FOR DASHBOARD
    # =========================================================

    completed_lesson_rows = db.execute(
        """
        SELECT course_id, COUNT(*) AS completed
        FROM lesson_progress
        WHERE user_id = ?
        GROUP BY course_id
        """,
        (user_id,)
    ).fetchall()

    lesson_progress = {}

    lesson_counts = {
        1: 5,
        2: 5,
        3: 5,
        4: 5
    }

    for row in completed_lesson_rows:

        course_id = row["course_id"]
        completed = row["completed"]
        total = lesson_counts.get(course_id, 0)

        percentage = 0

        if total > 0:
            percentage = round(
                (completed / total) * 100
            )

        lesson_progress[course_id] = {
            "completed": completed,
            "total": total,
            "percentage": percentage
        }

    db.close()

    return render_template(
        "dashboard.html",
        name=session.get("name"),
        total_users=total_users,
        total_courses=total_courses,
        total_questions=total_questions,
        completed_quizzes=completed_quizzes,
        average_score=quiz_stats["average_score"],
        best_score=quiz_stats["best_score"],
        recent_quizzes=recent_quizzes,
        lesson_progress=lesson_progress
    )
# =========================================================
# COURSES
# =========================================================

COURSES = [

    {
        "id": 1,
        "title": "Computer Fundamentals",
        "icon": "ðŸ’»",
        "level": "Beginner",
        "color": "blue",
        "description":
            "Learn computer basics, hardware, software, "
            "operating systems and internet fundamentals."
    },

    {
        "id": 2,
        "title": "MS Office",
        "icon": "ðŸ“Š",
        "level": "Beginner",
        "color": "green",
        "description":
            "Learn MS Word, Excel, PowerPoint and "
            "important office productivity skills."
    },

    {
        "id": 3,
        "title": "Python Programming",
        "icon": "ðŸ",
        "level": "Intermediate",
        "color": "yellow",
        "description":
            "Learn Python programming from variables "
            "to functions and projects."
    },

    {
        "id": 4,
        "title": "Web Development",
        "icon": "ðŸŒ",
        "level": "Intermediate",
        "color": "purple",
        "description":
            "Learn HTML, CSS and JavaScript to create "
            "modern websites."
    }

]


@app.route("/courses")
def courses():

    if not is_logged_in():

        return redirect(
            url_for("login")
        )

    return render_template(
        "courses.html",
        courses=COURSES
    )


# =========================================================
# COURSE DETAILS
# =========================================================

@app.route("/course/<int:course_id>")
def course(course_id):

    if not is_logged_in():

        return redirect(
            url_for("login")
        )

    course_data = next(
        (
            course
            for course in COURSES
            if course["id"] == course_id
        ),
        None
    )

    if not course_data:

        flash(
            "Course not found.",
            "danger"
        )

        return redirect(
            url_for("courses")
        )
    lessons = {

        1: [
            "Introduction to Computer",
            "Computer Hardware",
            "Computer Software",
            "Operating System",
            "Internet Basics"
        ],

        2: [
            "Microsoft Word",
            "Microsoft Excel",
            "Excel Formulas",
            "Microsoft PowerPoint",
            "Office Productivity"
        ],

        3: [
            "Python Introduction",
            "Variables and Data Types",
            "Operators",
            "Conditional Statements",
            "Loops",
            "Functions",
            "Lists",
            "Tuples",
            "Sets",
            "Dictionaries",
            "Strings",
            "String Methods",
            "List Methods",
            "Input and Output",
            "Type Casting",
            "Exception Handling",
            "File Handling",
            "Modules and Packages",
            "Object Oriented Programming",
            "Classes and Objects",
            "Inheritance",
            "Polymorphism",
            "Encapsulation",
            "Lambda Functions",
            "List Comprehension",
            "Python Projects",
            "Practice Exercises",
            "Final Python Project"
        ],

        4: [
            "HTML Basics",
            "CSS Styling",
            "JavaScript Basics",
            "Forms",
            "Responsive Websites"
        ]

    }

    db = get_db()

    completed_lessons = db.execute(
        """
        SELECT lesson_number
        FROM lesson_progress
        WHERE user_id = ? AND course_id = ?
        """,
        (
            session.get("user_id"),
            course_id
        )
    ).fetchall()

    db.close()

    completed_lessons = [
        row["lesson_number"]
        for row in completed_lessons
    ]

    return render_template(
        "course.html",
        course=course_data,
        lessons=lessons.get(
            course_id,
            []
        ),
        completed_lessons=completed_lessons
    )



# =========================================================
# LESSON PROGRESS
# =========================================================


# =========================================================
# QUIZ
# =========================================================

@app.route(
    "/quiz/<int:course_id>",
    methods=["GET", "POST"]
)
def quiz(course_id):

    if not is_logged_in():
        return redirect(url_for("login"))

    all_questions = load_questions()

    questions = [
        question
        for question in all_questions
        if int(question.get("course_id", 0)) == int(course_id)
    ]

    # सभी उपलब्ध questions इस course के लिए भेजें

    if not questions:
        flash(
            "No questions available.",
            "warning"
        )

        return redirect(
            url_for(
                "course",
                course_id=course_id
            )
        )

    if request.method == "POST":

        score = 0
        review = []

        for question in questions:

            question_id = str(
                question.get("id")
            )

            selected_answer = request.form.get(
                question_id
            )

            correct_answer = question.get("answer")

            is_correct = (
                selected_answer == correct_answer
            )

            if is_correct:
                score += 1

            review.append({
                "question": question.get("question"),
                "selected_answer": selected_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct
            })

        total = len(questions)

        percentage = round(
            (score / total) * 100,
            2
        )

        session["quiz_result"] = {
            "score": score,
            "total": total,
            "percentage": percentage,
            "review": review
        }

        db = get_db()

        db.execute(
            """
            INSERT INTO quiz_results
            (user_id, course_id, score, total)
            VALUES (?, ?, ?, ?)
            """,
            (
                session.get("user_id"),
                course_id,
                score,
                total
            )
        )

        db.commit()
        db.close()

        return redirect(
            url_for(
                "result",
                course_id=course_id
            )
        )

    course_data = next(
        (c for c in COURSES if c["id"] == course_id),
        None
    )

    if not course_data:
        flash("Course not found.", "danger")
        return redirect(url_for("courses"))

    return render_template(
        "quiz.html",
        questions=questions,
        course_id=course_id,
        course=course_data
    )

@app.route("/result/<int:course_id>")
def result(course_id):

    if not is_logged_in():

        return redirect(
            url_for("login")
        )

    result_data = session.get(
        "quiz_result"
    )

    if not result_data:

        return redirect(
            url_for("courses")
        )

    return render_template(
        "result.html",
        result=result_data,
        course_id=course_id
    )




# =========================================================
# ADMIN
# =========================================================

@app.route("/admin")
def admin():

    if not is_logged_in():

        return redirect(
            url_for("login")
        )

    if not is_admin():

        flash(
            "Admin access required.",
            "danger"
        )

        return redirect(
            url_for("dashboard")
        )

    db = get_db()

    users = db.execute(
        """
        SELECT
            id,
            name,
            email,
            role,
            created_at
        FROM users
        ORDER BY id DESC
        """
    ).fetchall()

    db.close()

    return render_template(
        "admin.html",
        users=users,
        courses=COURSES
    )


# =========================================================
# RUN SERVER
# =========================================================


# =========================================================
# LESSON PROGRESS
# =========================================================

@app.route("/complete-lesson", methods=["POST"])
def complete_lesson():

    if not is_logged_in():
        return {
            "success": False,
            "message": "Login required."
        }, 401

    course_id = request.form.get("course_id", type=int)
    lesson_number = request.form.get("lesson_number", type=int)

    if not course_id or not lesson_number:
        return {
            "success": False,
            "message": "Invalid lesson data."
        }, 400

    db = get_db()

    db.execute(
        """
        INSERT OR IGNORE INTO lesson_progress
        (user_id, course_id, lesson_number)
        VALUES (?, ?, ?)
        """,
        (
            session.get("user_id"),
            course_id,
            lesson_number
        )
    )

    db.commit()
    db.close()

    return {
        "success": True,
        "message": "Lesson completed successfully!"
    }



# =========================================================
# LESSON PROGRESS
# =========================================================


if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )

# =========================================================
# LESSON PROGRESS
# =========================================================


# =========================================================
# QUIZ
# =========================================================





















