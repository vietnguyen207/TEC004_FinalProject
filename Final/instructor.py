import sqlite3
from flask import Blueprint, render_template, request, redirect, session
from decorator import login_required
from decorator import instructor_required
instructor_bp = Blueprint("instructor", __name__)
DATABASE = "database_fp.db"



def get_my_courses(instructor_id):

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            c.course_id,
            c.course_name,
            c.semester,
            COUNT(e.student_id) AS total_students

        FROM courses c

        JOIN enrollments e
            ON c.course_id = e.course_id

        WHERE e.instructor_id = ?

        GROUP BY
            c.course_id,
            c.course_name,
            c.semester

        ORDER BY c.course_name
    """,(instructor_id,))

    data = cursor.fetchall()

    conn.close()

    return data
    
@instructor_bp.route("/instructor_db")
@login_required
@instructor_required
def dashboard():

    instructor_id = session["user_id"]

    courses = get_my_courses(instructor_id)

    total_course = len(courses)

    total_student = sum(course["total_students"] for course in courses)

    return render_template(
        "instructor_page/dashboard.html",
        instructor=session["username"],
        courses=courses,
        total_course=total_course,
        total_student=total_student
    )