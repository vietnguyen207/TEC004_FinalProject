import sqlite3

DATABASE = "database_fp.db"


def get_connection():

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    return conn

def get_student_profile(student_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM students

        WHERE student_id=?

    """,(student_id,))

    student = cursor.fetchone()

    conn.close()

    return student


def get_my_courses(student_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            c.course_id,
            c.course_name,
            c.credits,
            c.semester,
            c.sessions

        FROM enrollments e

        JOIN courses c

        ON e.course_id=c.course_id

        WHERE e.student_id=?

        ORDER BY c.course_name

    """,(student_id,))

    courses = cursor.fetchall()

    conn.close()

    return courses


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

def student_owns_course(student_id, course_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM enrollments

        WHERE

        student_id=?

        AND

        course_id=?

    """,(student_id,course_id))

    result = cursor.fetchone()

    conn.close()

    return result is not None

def get_my_attendance(student_id, course_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            session_number,
            status,
            attendance_date

        FROM attendance_records

        WHERE

            student_id=?

        AND

            course_id=?

        ORDER BY session_number

    """,(student_id,course_id))

    rows = cursor.fetchall()

    conn.close()

    return rows

def get_attendance_rate(student_id, course_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT attendance_rate

        FROM attendance

        WHERE

            student_id=?

        AND

            course_id=?

    """,(student_id,course_id))

    row = cursor.fetchone()

    conn.close()

    if row:

        return row["attendance_rate"]

    return 0

def attendance_report(student_id,course_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            session_number,

            status,

            attendance_date

        FROM attendance_records

        WHERE

            student_id=?

        AND

            course_id=?

        ORDER BY session_number

    """,(student_id,course_id))

    report = cursor.fetchall()

    conn.close()

    return report

def attendance_summary(student_id, course_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            status

        FROM attendance_records

        WHERE

            student_id=?

        AND

            course_id=?

    """,(student_id,course_id))

    rows = cursor.fetchall()

    conn.close()

    summary = {

        "present":0,

        "late":0,

        "absent":0,

        "total":0

    }

    for row in rows:

        status = row["status"]

        summary["total"] += 1

        if status == "Present":

            summary["present"] += 1

        elif status == "Late":

            summary["late"] += 1

        elif status == "Absent":

            summary["absent"] += 1

    return summary

def get_my_grades(student_id, course_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            assignment,
            midterm,
            final,
            final_grade

        FROM grades

        WHERE

            student_id=?

        AND

            course_id=?

    """,(student_id,course_id))

    grade = cursor.fetchone()

    conn.close()

    return grade

def grade_report(student_id, course_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            c.course_name,
            c.semester,
            c.credits,

            g.assignment,
            g.midterm,
            g.final,
            g.final_grade,

            gs.assignment_weight,
            gs.midterm_weight,
            gs.final_weight

        FROM grades g

        JOIN courses c
        ON g.course_id = c.course_id

        LEFT JOIN grading_scheme gs
        ON gs.course_id = g.course_id

        WHERE

            g.student_id = ?

        AND

            g.course_id = ?

    """,(student_id,course_id))

    report = cursor.fetchone()

    conn.close()

    return report

def get_homework_scores(student_id, course_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            a.assignment_name,
            a.assignment_type,
            a.due_date,
            a.max_points,

            s.score,
            s.feedback,
            s.status,
            s.submit_time

        FROM assignments a

        LEFT JOIN assignment_submissions s

        ON a.assignment_id = s.assignment_id
        AND s.student_id = ?

        WHERE a.course_id = ?

        ORDER BY

            CASE a.assignment_type
                WHEN 'assignment' THEN 1
                WHEN 'midterm' THEN 2
                WHEN 'final' THEN 3
                ELSE 4
            END,

            a.assignment_id

    """,(student_id, course_id))

    rows = cursor.fetchall()

    conn.close()

    return rows

def calculate_my_gpa(student_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            c.semester,

            SUM(g.final_grade*c.credits) AS total_score,

            SUM(c.credits) AS total_credit

        FROM grades g

        JOIN courses c

        ON g.course_id=c.course_id

        WHERE

            g.student_id=?

        GROUP BY c.semester

        ORDER BY c.semester

    """,(student_id,))

    rows = cursor.fetchall()

    conn.close()

    gpas=[]

    for row in rows:

        if row["total_credit"]==0:

            gpa=0

        else:

            gpa=round(

                row["total_score"]/

                row["total_credit"],

                2

            )

        gpas.append({

            "semester":row["semester"],

            "gpa":gpa

        })

    return gpas


def get_attendance_statistics(student_id):

    conn=get_connection()

    cursor=conn.cursor()

    cursor.execute("""

        SELECT

            AVG(attendance_rate)

        FROM attendance

        WHERE student_id=?

    """,(student_id,))

    avg=cursor.fetchone()[0]

    conn.close()

    return avg

def get_grade_statistics(student_id):

    conn=get_connection()

    cursor=conn.cursor()

    cursor.execute("""

        SELECT

            AVG(final_grade),

            MAX(final_grade),

            MIN(final_grade)

        FROM grades

        WHERE student_id=?

    """,(student_id,))

    data=cursor.fetchone()

    conn.close()

    return data

# Get assignment of the course
def get_course_assignments(course_id, student_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            a.*,
            COALESCE(sub.status, 'Not Submitted') AS status
        FROM assignments a
        LEFT JOIN assignment_submissions sub 
            ON a.assignment_id = sub.assignment_id 
            AND sub.student_id = ?
        WHERE a.course_id = ?
        ORDER BY a.due_date
    """, (student_id, course_id))

    assignments = cursor.fetchall()
    conn.close()
    return assignments
# Get student's assignment submission
def get_my_submission(student_id, assignment_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM assignment_submissions

        WHERE

            student_id=?

        AND

            assignment_id=?

    """,(student_id,assignment_id))

    submission = cursor.fetchone()

    conn.close()

    return submission
# Update student's assignment submission
def submit_assignment(

        assignment_id,

        student_id,

        file_name,

        file_path

):

    conn=get_connection()

    cursor=conn.cursor()

    cursor.execute("""

        UPDATE assignment_submissions

        SET

            submit_time=CURRENT_TIMESTAMP,

            file_name=?,

            file_path=?,

            status='Submitted'

        WHERE

            assignment_id=?

        AND

            student_id=?

    """,(

        file_name,

        file_path,

        assignment_id,

        student_id

    ))

    conn.commit()

    conn.close()

def get_assignment(assignment_id):

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM assignments

        WHERE assignment_id=?

    """,(assignment_id,))

    assignment = cursor.fetchone()

    conn.close()

    return assignment

