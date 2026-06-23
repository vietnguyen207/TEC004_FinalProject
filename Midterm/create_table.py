
import sqlite3


DATABASE = "database_fp.db"

def create_database():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students(
        student_id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT,
        major TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS instructors(
        instructor_id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT,
        department TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses(
        course_id TEXT PRIMARY KEY,
        course_name TEXT,
        credits INTEGER,
        semester TEXT,
        sessions INTEGER
    )
    """)

    cursor.execute("""
CREATE TABLE IF NOT EXISTS enrollments(
    enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    course_id TEXT,
    instructor_id TEXT,
    FOREIGN KEY(student_id)
        REFERENCES students(student_id),

    FOREIGN KEY(course_id)
        REFERENCES courses(course_id),
                   
    FOREIGN KEY(instructor_id)
        REFERENCES instructors(instructor_id)
)
""")
    cursor.execute("""
CREATE TABLE IF NOT EXISTS grades(
    grade_id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id TEXT,
    course_id TEXT,

    assignment REAL,
    midterm REAL,
    final REAL,

    final_grade REAL,

    FOREIGN KEY(student_id)
        REFERENCES students(student_id),

    FOREIGN KEY(course_id)
        REFERENCES courses(course_id)
    UNIQUE(student_id, course_id)
)
""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance_records(

    record_id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id TEXT,

    course_id TEXT,

    session_number INTEGER,

    status TEXT,

    attendance_date DATE,

    FOREIGN KEY(student_id)
        REFERENCES students(student_id),

    FOREIGN KEY(course_id)
        REFERENCES courses(course_id))
""")
    conn.commit()
    conn.close()