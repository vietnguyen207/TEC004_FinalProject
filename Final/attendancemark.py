import sqlite3
DB_NAME = "database_fp.db"
def mark_attendance(
    student_id,
    course_id,
    session_number,
    status
):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO attendance_records(
            student_id,
            course_id,
            session_number,
            status,
            attendance_date
        )

        VALUES(
            ?,
            ?,
            ?,
            ?,
            DATE('now')
        )
    """,
    (
        student_id,
        course_id,
        session_number,
        status
    ))

    conn.commit()

    conn.close()

def update_attendance_rate(
    student_id,
    course_id
):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)

        FROM attendance_records

        WHERE student_id=?
        AND course_id=?
        AND status='Present'
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
    """,
    (
        course_id,
    ))

    total_sessions = cursor.fetchone()[0]

    attendance_rate = (
        present
        /
        total_sessions
    ) * 100

    cursor.execute("""
        INSERT OR REPLACE INTO attendance(
            student_id,
            course_id,
            attendance_rate
        )

        VALUES(
            ?,
            ?,
            ?
        )
    """,
    (
        student_id,
        course_id,
        attendance_rate
    ))

    conn.commit()

    conn.close()

    return attendance_rate