
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
    UNIQUE(student_id, course_id)
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
    CREATE TABLE IF NOT EXISTS attendance(

    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id TEXT,

    course_id TEXT,

    attendance_rate REAL,

    FOREIGN KEY(student_id)
        REFERENCES students(student_id),

    FOREIGN KEY(course_id)
        REFERENCES courses(course_id),

    UNIQUE(student_id, course_id))
""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance_records(
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id TEXT NOT NULL,
    course_id TEXT NOT NULL,    

    session_number INTEGER NOT NULL,

    attendance_date DATE,

    status TEXT CHECK(status IN ('Present','Late','Absent')),

    UNIQUE(student_id, course_id, session_number),

    FOREIGN KEY(student_id) REFERENCES students(student_id),
    FOREIGN KEY(course_id) REFERENCES courses(course_id))
""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assignments(

    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,

    course_id TEXT NOT NULL,

    assignment_name TEXT NOT NULL,

    assignment_type TEXT NOT NULL,

    description TEXT,

    due_date DATE,

    max_points REAL,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(course_id)
    REFERENCES courses(course_id))
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assignment_submissions(

    submission_id INTEGER PRIMARY KEY AUTOINCREMENT,

    assignment_id INTEGER NOT NULL,

    student_id TEXT NOT NULL,

    course_id TEXT NOT NULL,

    submit_time DATETIME,

    file_name TEXT,

    file_path TEXT,

    score REAL,

    feedback TEXT,

    status TEXT DEFAULT 'Not Submitted',

    attempt INTEGER DEFAULT 1,

    FOREIGN KEY(assignment_id)
        REFERENCES assignments(assignment_id),

    FOREIGN KEY(student_id)
        REFERENCES students(student_id),

    FOREIGN KEY(course_id)
        REFERENCES courses(course_id),
    UNIQUE(
        assignment_id,
        student_id
    )
)
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS grading_scheme(

    scheme_id INTEGER PRIMARY KEY AUTOINCREMENT,

    course_id TEXT,
    instructor_id TEXT,

    assignment_weight REAL,
    midterm_weight REAL,
    final_weight REAL,

    FOREIGN KEY(course_id)
        REFERENCES courses(course_id),

    FOREIGN KEY(instructor_id)
        REFERENCES instructors(instructor_id),

    UNIQUE(course_id, instructor_id))
""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

    username TEXT PRIMARY KEY,

    password TEXT NOT NULL,

    role TEXT NOT NULL,

    user_id TEXT NOT NULL)

""")
    conn.commit()
    conn.close()