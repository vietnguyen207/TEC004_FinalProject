import sqlite3
from datetime import datetime
DATABASE = "database_fp.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_my_courses(instructor_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            c.course_id,

            c.course_name,

            c.semester,

            c.credits,

            c.sessions,

            COUNT(e.student_id) AS total_students

        FROM courses c

        JOIN enrollments e

            ON c.course_id = e.course_id

        WHERE e.instructor_id = ?

        GROUP BY

            c.course_id,

            c.course_name,

            c.semester,

            c.credits,

            c.sessions

        ORDER BY c.course_name

    """,(instructor_id,))

    data = cursor.fetchall()

    conn.close()

    return data

def get_course(course_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM courses

        WHERE course_id=?

    """,(course_id,))

    course = cursor.fetchone()

    conn.close()

    return course

def instructor_owns_course(instructor_id, course_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT 1

        FROM enrollments

        WHERE instructor_id=?

        AND course_id=?

        LIMIT 1

    """,(instructor_id,course_id))

    result = cursor.fetchone()

    conn.close()

    return result is not None

def get_total_sessions(course_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT sessions

        FROM courses

        WHERE course_id=?

    """,(course_id,))

    row = cursor.fetchone()

    conn.close()

    return row["sessions"]

def get_students(course_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            s.student_id,

            s.name

        FROM students s

        JOIN enrollments e

            ON s.student_id=e.student_id

        WHERE e.course_id=?

        ORDER BY s.name

    """,(course_id,))

    students=cursor.fetchall()

    conn.close()

    return students

def load_attendance(course_id,session_number):

    conn=get_connection()

    cursor=conn.cursor()

    cursor.execute("""

        SELECT

            student_id,

            status

        FROM attendance_records

        WHERE course_id=?

        AND session_number=?

    """,(course_id,session_number))

    rows=cursor.fetchall()

    conn.close()

    return{

        row["student_id"]:row["status"]

        for row in rows

    }

def save_attendance(course_id, session_number, attendance_data):

    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    for student_id, status in attendance_data.items():

        cursor.execute("""
            SELECT record_id
            FROM attendance_records
            WHERE student_id = ?
            AND course_id = ?
            AND session_number = ?
        """, (student_id, course_id, session_number))

        record = cursor.fetchone()

        if record:

            cursor.execute("""
                UPDATE attendance_records
                SET status = ?,
                    date = ?
                WHERE record_id = ?
            """, (status, today, record["record_id"]))

        else:

            cursor.execute("""
                INSERT INTO attendance_records
                (
                    student_id,
                    course_id,
                    session_number,
                    status,
                    attendance_date
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                student_id,
                course_id,
                session_number,
                status,
                today
            ))

    conn.commit()
    conn.close()

def update_attendance_rate(course_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sessions
        FROM courses
        WHERE course_id = ?
    """, (course_id,))

    total_sessions = cursor.fetchone()["sessions"]

    cursor.execute("""
        SELECT DISTINCT student_id
        FROM attendance_records
        WHERE course_id = ?
    """, (course_id,))

    students = cursor.fetchall()

    for student in students:

        student_id = student["student_id"]

        cursor.execute("""
            SELECT COUNT(*)
            FROM attendance_records
            WHERE student_id = ?
            AND course_id = ?
            AND status = 'Present'
        """, (student_id, course_id))

        present = cursor.fetchone()[0]

        attendance_rate = round(
            present * 100 / total_sessions,
            2
        )

        cursor.execute("""
            SELECT attendance_id
            FROM attendance
            WHERE student_id = ?
            AND course_id = ?
        """, (student_id, course_id))

        row = cursor.fetchone()

        if row:

            cursor.execute("""
                UPDATE attendance
                SET attendance_rate = ?
                WHERE attendance_id = ?
            """, (
                attendance_rate,
                row["attendance_id"]
            ))

        else:

            cursor.execute("""
                INSERT INTO attendance
                (
                    student_id,
                    course_id,
                    attendance_rate
                )
                VALUES (?, ?, ?)
            """, (
                student_id,
                course_id,
                attendance_rate
            ))

    conn.commit()
    conn.close()

def get_attendance_history(course_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            ar.session_number,

            s.student_id,

            s.name,

            ar.status,

            ar.date

        FROM attendance_records ar

        JOIN students s

        ON ar.student_id=s.student_id

        WHERE ar.course_id=?

        ORDER BY

        ar.session_number,

        s.name

    """,(course_id,))

    rows=cursor.fetchall()

    conn.close()

    return rows

def attendance_report_page(course_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            s.student_id,

            s.name,

            a.attendance_rate

        FROM attendance a

        JOIN students s

        ON a.student_id=s.student_id

        WHERE a.course_id=?

        ORDER BY a.attendance_rate DESC

    """,(course_id,))

    rows=cursor.fetchall()

    conn.close()

    return rows


def get_gradebook(course_id):

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT

            s.student_id,
            s.name,

            g.assignment,
            g.midterm,
            g.final,
            g.final_grade

        FROM enrollments e

        JOIN students s

        ON e.student_id=s.student_id

        LEFT JOIN grades g

        ON g.student_id=s.student_id

        AND g.course_id=e.course_id

        WHERE e.course_id=?

        ORDER BY s.name
    """,(course_id,))

    data=cursor.fetchall()

    conn.close()

    return data

def get_student_grade(student_id,course_id):

    conn=sqlite3.connect(DATABASE)

    conn.row_factory=sqlite3.Row

    cursor=conn.cursor()

    cursor.execute("""

        SELECT *

        FROM grades

        WHERE student_id=?

        AND course_id=?

    """,(student_id,course_id))

    row=cursor.fetchone()

    conn.close()

    return row

def update_grade(

    student_id,

    course_id,

    assignment,

    midterm,

    final

):

    conn=sqlite3.connect(DATABASE)

    cursor=conn.cursor()

    cursor.execute("""

        UPDATE grades

        SET

            assignment=?,

            midterm=?,

            final=?

        WHERE

            student_id=?

            AND course_id=?

    """,(assignment,

         midterm,

         final,

         student_id,

         course_id))

    conn.commit()

    conn.close()

def get_weight(course_id,instructor_id):

    conn=sqlite3.connect(DATABASE)

    conn.row_factory=sqlite3.Row

    cursor=conn.cursor()

    cursor.execute("""

        SELECT *

        FROM grading_scheme

        WHERE course_id=?
        AND instructor_id=?
    """,(course_id,instructor_id))

    row=cursor.fetchone()

    conn.close()

    return row

def update_weight(

course_id, 

instructor_id,

assignment,

midterm,

final

):

    conn=sqlite3.connect(DATABASE)

    cursor=conn.cursor()

    cursor.execute("""

        UPDATE grading_scheme

        SET

            assignment_weight=?,

            midterm_weight=?,

            final_weight=?

        WHERE course_id=?
        AND instructor_id=?

    """,(assignment,

         midterm,

         final,

         course_id,
         instructor_id))

    conn.commit()

    conn.close()

def calculate_final_grade(course_id):

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            assignment_weight,
            midterm_weight,
            final_weight

        FROM grading_scheme

        WHERE course_id=?

    """,(course_id,))

    weight=cursor.fetchone()

    assignment_weight=weight["assignment_weight"]/100
    midterm_weight=weight["midterm_weight"]/100
    final_weight=weight["final_weight"]/100

    cursor.execute("""

        SELECT *

        FROM grades

        WHERE course_id=?

    """,(course_id,))

    grades=cursor.fetchall()

    for grade in grades:

        final_grade=(

            grade["assignment"]*assignment_weight+

            grade["midterm"]*midterm_weight+

            grade["final"]*final_weight

        )

        cursor.execute("""

            UPDATE grades

            SET final_grade=?

            WHERE grade_id=?

        """,(round(final_grade,2),

             grade["grade_id"]))

    conn.commit()

    conn.close()


def get_session_status(course_id):

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            session_number

        FROM attendance_records

        WHERE course_id=?

        GROUP BY session_number

    """,(course_id,))

    rows = cursor.fetchall()

    conn.close()

    completed = []

    for row in rows:
        completed.append(row["session_number"])

    return completed

# Get All assignments for a course
def get_assignments(course_id):

    conn=get_connection()

    cursor=conn.cursor()

    cursor.execute("""

        SELECT *

        FROM assignments

        WHERE course_id=?

        ORDER BY due_date

    """,(course_id,))

    assignments=cursor.fetchall()

    conn.close()

    return assignments

# Get a specific assignment by its ID
def get_assignment(assignment_id):

    conn=get_connection()

    cursor=conn.cursor()

    cursor.execute("""

        SELECT *

        FROM assignments

        WHERE assignment_id=?

    """,(assignment_id,))

    assignment=cursor.fetchone()

    conn.close()

    return assignment

# Automatically create submission records for all students enrolled in a course when a new assignment is created
def create_submission_records(assignment_id, course_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT student_id

        FROM enrollments

        WHERE course_id=?

    """,(course_id,))

    students = cursor.fetchall()

    for student in students:

        cursor.execute("""

            INSERT INTO assignment_submissions(

                assignment_id,

                student_id,

                course_id,

                status

            )

            VALUES(?,?,?,?)

        """,(

            assignment_id,

            student["student_id"],

            course_id,

            "Not Submitted"

        ))

    conn.commit()

    conn.close()

# Create a new assignment for a course
def create_assignment(

        course_id,

        assignment_name,

        assignment_type,

        description,

        due_date,

        max_points

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        INSERT INTO assignments(

            course_id,

            assignment_name,

            assignment_type,

            description,

            due_date,

            max_points

        )

        VALUES(?,?,?,?,?,?)

    """,(

        course_id,

        assignment_name,

        assignment_type,

        description,

        due_date,

        max_points

    ))

    assignment_id = cursor.lastrowid

    conn.commit()

    conn.close()

    create_submission_records(

        assignment_id,

        course_id

    )
# Update an existing assignment's details
def update_assignment(

        assignment_id,

        assignment_name,

        assignment_type,

        description,

        due_date,

        max_points

):

    conn=get_connection()

    cursor=conn.cursor()

    cursor.execute("""

        UPDATE assignments

        SET

        assignment_name=?,

        assignment_type=?,

        description=?,

        due_date=?,

        max_points=?

        WHERE assignment_id=?

    """,(

        assignment_name,

        assignment_type,

        description,

        due_date,

        max_points,

        assignment_id

    ))

    conn.commit()

    conn.close()

# Delete an assignment by its ID
def delete_assignment(assignment_id):

    conn=get_connection()

    cursor=conn.cursor()

    cursor.execute("""

        DELETE

        FROM assignments

        WHERE assignment_id=?

    """,(assignment_id,))

    conn.commit()

    conn.close()

def get_submissions(assignment_id):

    conn=get_connection()

    conn.row_factory=sqlite3.Row

    cursor=conn.cursor()

    cursor.execute("""

        SELECT

            s.student_id,

            s.name,

            sub.*

        FROM assignment_submissions sub

        JOIN students s

        ON sub.student_id=s.student_id

        WHERE sub.assignment_id=?

        ORDER BY s.name

    """,(assignment_id,))

    data=cursor.fetchall()

    conn.close()

    return data

def get_submission(submission_id):

    conn=get_connection()

    conn.row_factory=sqlite3.Row

    cursor=conn.cursor()

    cursor.execute("""

        SELECT *

        FROM assignment_submissions

        WHERE submission_id=?

    """,(submission_id,))

    submission=cursor.fetchone()

    conn.close()

    return submission

def grade_submission(

        submission_id,

        score,

        feedback

):

    conn=get_connection()

    cursor=conn.cursor()

    cursor.execute("""

        UPDATE assignment_submissions

        SET

            score=?,

            feedback=?,

            status='Graded'

        WHERE submission_id=?

    """,(

        score,

        feedback,

        submission_id

    ))

    conn.commit()

    conn.close()

def calculate_assignment_average(

        student_id,

        course_id

):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            a.assignment_type,
            AVG(sub.score) AS avg_score
        FROM assignment_submissions sub
        JOIN assignments a
            ON sub.assignment_id = a.assignment_id
        WHERE
            sub.student_id = ?
            AND a.course_id = ?
            AND sub.status = 'Graded'
        GROUP BY a.assignment_type
    """, (student_id, course_id))

    rows = cursor.fetchall()

    conn.close()

    averages = {
        "assignment": 0,
        "midterm": 0,
        "final": 0
    }

    for assignment_type, avg_score in rows:
        averages[assignment_type] = avg_score
    
    return averages

def update_assignment_grade(

        student_id,

        course_id

):

    averages = calculate_assignment_average(
        student_id,
        course_id
    )

    assignment = averages.get("assignment", 0)
    midterm = averages.get("midterm", 0)
    final = averages.get("final", 0)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE grades
        SET
            assignment = ?,
            midterm = ?,
            final = ?
        WHERE
            student_id = ?
            AND course_id = ?
    """, (
        assignment,
        midterm,
        final,
        student_id,
        course_id
    ))

    conn.commit()
    conn.close()