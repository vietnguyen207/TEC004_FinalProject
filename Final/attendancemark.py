import sqlite3

DATABASE = "database_fp.db"
def get_students(course_id):

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

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

    students = cursor.fetchall()

    conn.close()

    return students

def save_attendance(student_id,
                    course_id,
                    session_number,
                    attendance_date,
                    status):

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO attendance_records(

        student_id,

        course_id,

        session_number,

        attendance_date,

        status

    )

    VALUES(?,?,?,?,?)

    ON CONFLICT(student_id,course_id,session_number)

    DO UPDATE SET

        attendance_date=excluded.attendance_date,

        status=excluded.status

    """,

    (

        student_id,

        course_id,

        session_number,

        attendance_date,

        status

    ))

    conn.commit()

    conn.close()

def load_attendance(course_id,
                    session_number):

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

    SELECT

        s.student_id,

        s.name,

        ar.status

    FROM students s

    JOIN enrollments e

        ON s.student_id=e.student_id

    LEFT JOIN attendance_records ar

        ON

        ar.student_id=s.student_id

        AND

        ar.course_id=e.course_id

        AND

        ar.session_number=?

    WHERE e.course_id=?

    ORDER BY s.name

    """,

    (

        session_number,

        course_id

    ))

    data = cursor.fetchall()

    conn.close()

    return data

def calculate_attendance_rate(student_id,
                              course_id):

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()
    cursor.execute("""

    SELECT COUNT(*)

    FROM attendance_records

    WHERE

        student_id=?

        AND

        course_id=?

        AND

        status='Present'

    """,

    (

        student_id,

        course_id

    ))

    present = cursor.fetchone()[0]
    cursor.execute("""

    SELECT sessions

    FROM courses

    WHERE course_id=?

    """,(course_id,))

    total = cursor.fetchone()[0]

    rate = present/total*100

    cursor.execute("""

    INSERT INTO attendance(

        student_id,

        course_id,

        attendance_rate

    )

    VALUES(?,?,?)

    ON CONFLICT(student_id,course_id)

    DO UPDATE SET

    attendance_rate=excluded.attendance_rate

    """,

    (

        student_id,

        course_id,

        rate

    ))

    conn.commit()

    conn.close()

    return rate

def update_attendance_rate(course_id):

    conn=sqlite3.connect(DATABASE)

    cursor=conn.cursor()

    cursor.execute("""

    SELECT sessions

    FROM courses

    WHERE course_id=?

    """,(course_id,))

    total_sessions=cursor.fetchone()[0]

    cursor.execute("""

    SELECT DISTINCT student_id

    FROM attendance_records

    WHERE course_id=?

    """,(course_id,))

    students=cursor.fetchall()

    for s in students:

        student=s[0]

        cursor.execute("""

        SELECT COUNT(*)

        FROM attendance_records

        WHERE

        student_id=?

        AND course_id=?

        AND status='Present'

        """,

        (

            student,

            course_id

        ))

        present=cursor.fetchone()[0]

        rate=round(

            present*100/total_sessions,

            2

        )

        cursor.execute("""

        INSERT INTO attendance(

            student_id,

            course_id,

            attendance_rate

        )

        VALUES(?,?,?)

        ON CONFLICT(student_id,course_id)

        DO UPDATE SET

        attendance_rate=excluded.attendance_rate

        """,

        (

            student,

            course_id,

            rate

        ))

    conn.commit()

    conn.close()