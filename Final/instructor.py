import sqlite3
from flask import Blueprint, render_template, request, redirect, session

instructor_bp = Blueprint("instructor", __name__)
DATABASE = "database_fp.db"
@instructor_bp.route("/dashboard")

def dashboard():


    instructor_id = session["instructor_id"]

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # Fetch instructor information
    cursor.execute("""

    SELECT *

    FROM instructors

    WHERE instructor_id=?

    """,(instructor_id,))

    info = cursor.fetchone()

    # Fetch total courses and students taught by the instructor
    cursor.execute("""

    SELECT COUNT(DISTINCT course_id)

    FROM enrollments

    WHERE instructor_id=?

    """,(instructor_id,))

    total_courses = cursor.fetchone()[0]

    # Fetch total students taught by the instructor
    cursor.execute("""

    SELECT COUNT(DISTINCT student_id)

    FROM enrollments

    WHERE instructor_id=?

    """,(instructor_id,))

    total_students = cursor.fetchone()[0]