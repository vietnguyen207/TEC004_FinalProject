from BaseClasses import Student, Instructor, Course, WeightedGrading
from decorator import login_required
from decorator import admin_required
from pd_analytics import calculate_gpa, class_ranking
from matplotlib_charts import grade_distribution, gpa_trend,course_difficulty,performance_radar
from attendancemark import update_attendance_rate
import pandas as pd
from datetime import date
from flask import Blueprint, url_for
from flask import render_template
from flask import request
from flask import redirect
from flask import send_file
from flask import flash
import sqlite3
import os
from create_table import DATABASE
from CSV_JSON import (import_multiple_csv, export_report_json)

admin_bp = Blueprint("admin", __name__)


# -------------------------
# Loading UI/UX Function
# ------------------------
@admin_bp.route("/admin")
@login_required
@admin_required
def dashboard():
   
    return render_template("admin_page/admin.html")

# ----------------------------------------------------------
# Add and Store Student Information (ID, Name, Email, Major)
# ----------------------------------------------------------

@admin_bp.route("/student", methods=["GET","POST"])
@login_required
@admin_required
def student():

    if request.method == "POST":

        student = Student(
            request.form["id"],
            request.form["name"],
            request.form["email"],
            request.form["major"]
        )

        conn = sqlite3.connect(DATABASE)

        cursor = conn.cursor()
        error_student_id = ""

        cursor.execute(
    "SELECT * FROM students WHERE student_id=?",
    (student.id,)
)

        if cursor.fetchone():
            error_student_id = "Student ID already exists"

            return render_template(
                    "student.html",
                    student=student,
                    error_student_id=error_student_id
    )
        else:
            cursor.execute("""
        INSERT INTO students
        VALUES(?,?,?,?)
        """,
        (
            student.id,
            student.name,
            student.email,
            student.major
        ))

        conn.commit()
        conn.close()

        return redirect("/student")

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM students
    """)

    students = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_page/manage_stu.html",
        students=students
    )

# ------------------------------------------------------------------
# Add and Store Instructor Information (ID, Name, Email, Department)
# ------------------------------------------------------------------

@admin_bp.route("/instructor", methods=["GET","POST"])
@login_required
@admin_required
def instructor():

    if request.method == "POST":

        instructor = Instructor(
            request.form["id"],
            request.form["name"],
            request.form["email"],
            request.form["department"]
        )

        conn = sqlite3.connect(DATABASE)

        cursor = conn.cursor()
        error_instructor_id = ""

        cursor.execute(
    "SELECT * FROM instructors WHERE instructor_id=?",
    (instructor.id,)
)

        if cursor.fetchone():
            error_instructor_id = "Instructor ID already exists"

            return render_template(
                    "instructor.html",
                    instructor=instructor,
                    error_instructor_id=error_instructor_id
    )
        else:
            cursor.execute("""
        INSERT INTO instructors
        VALUES(?,?,?,?)
        """,
        (
            instructor.id,
            instructor.name,
            instructor.email,
            instructor.department
        ))

        conn.commit()
        conn.close()

        return redirect("/instructor")

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM instructors
    ORDER BY instructor_id
""")

    instructors = cursor.fetchall()

    conn.close()

    return render_template(
    "admin_page/manage_instru.html",
    instructors=instructors
)

# ----------------------------------------------------------
# Add and Store Grading Scheme Information (Assignment, Midterm, Final)
# ----------------------------------------------------------
@admin_bp.route(
"/grading_scheme/<instructor_id>",
methods=["GET","POST"]
)
@login_required
@admin_required
def edit_grade_scheme(instructor_id):

    if request.method=="POST":

        course_id=request.form["course_id"]

        assignment=float(
            request.form["assignment"]
        )

        midterm=float(
            request.form["midterm"]
        )

        final=float(
            request.form["final"]
        )

        if assignment+midterm+final!=100:

            return "Total percentage must equal 100"
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("""

        INSERT INTO grading_scheme(

            course_id,

            instructor_id,

            assignment_weight,

            midterm_weight,

            final_weight

        )

        VALUES(?,?,?,?,?)

        ON CONFLICT(course_id,instructor_id)

        DO UPDATE SET

        assignment_weight=excluded.assignment_weight,

        midterm_weight=excluded.midterm_weight,

        final_weight=excluded.final_weight

        """,

        (

            course_id,

            instructor_id,

            assignment,

            midterm,

            final

        ))

        conn.commit()

        return redirect(
        url_for(
            "admin.edit_grade_scheme",
            instructor_id=instructor_id
        )
    )
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

    SELECT DISTINCT

        c.course_id,

        c.course_name,

        gs.assignment_weight,

        gs.midterm_weight,

        gs.final_weight

    FROM courses c

    JOIN enrollments e

        ON c.course_id=e.course_id

    LEFT JOIN grading_scheme gs

        ON

        gs.course_id=c.course_id

        AND

        gs.instructor_id=e.instructor_id

    WHERE

        e.instructor_id=?

    ORDER BY c.course_name

    """,(instructor_id,))

    courses = cursor.fetchall()

    conn.close()

    return render_template(

        "admin_page/grading_scheme.html",

        courses=courses,

        instructor_id=instructor_id

    )
# ----------------------------------------------------------------------------------
# Add and Store Course Information (ID, Name, Credits, Semester, Number of Sessions)
# ----------------------------------------------------------------------------------

@admin_bp.route("/course", methods=["GET","POST"])
@login_required
@admin_required
def course():

    if request.method == "POST":

        course = Course(
            request.form["id"],
            request.form["name"],
            request.form["credits"],
            request.form["semester"],
            request.form["sessions"]
        )

        conn = sqlite3.connect(DATABASE)

        cursor = conn.cursor()
        error_course_id = ""

        cursor.execute(
    "SELECT * FROM courses WHERE course_id=?",
    (course.id,)
)

        if cursor.fetchone():
            error_course_id = "Course ID already exists"

            return render_template(
                    "admin_page/manage_course.html",
                    course=course,
                    error_course_id=error_course_id
    )
        else:
            cursor.execute("""
                INSERT INTO courses
                VALUES(?,?,?,?,?)
                """,
                (
                course.id,
                course.name,
                course.credits,
                course.semester,
                course.sessions
            ))
        conn.commit()
        conn.close()
    
        return redirect("/course")

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM courses
    """)

    courses = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_page/manage_course.html",
        courses=courses
    )


# ---------------------------------------------
# Manage data between student, course, and instructor
# ---------------------------------------------

@admin_bp.route("/enrollment", methods=["GET","POST"])
@login_required
@admin_required
def enrollment():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if request.method == "POST":

        student_id = request.form["student_id"]
        course_id = request.form["course_id"]
        instructor_id = request.form["instructor_id"]

        try:

            # enroll student
            cursor.execute("""
                INSERT INTO enrollments
                (student_id, course_id, instructor_id)
                VALUES (?, ?, ?)
            """, (
                student_id,
                course_id,
                instructor_id
            ))
            # create percentage of grade record
            cursor.execute("""
                INSERT OR IGNORE INTO grading_scheme(
                    course_id,
                    instructor_id,
                    assignment_weight,
                    midterm_weight,
                    final_weight
                                    )
                    VALUES(?,?,?,?,?)
                        """,
                    (
                        course_id,
                        instructor_id,
                        20,   # mặc định
                        30,
                        50
                    ))
            # create grade record
            cursor.execute("""
                INSERT OR IGNORE INTO grades
                (
                    student_id,
                    course_id,
                    assignment,
                    midterm,
                    final,
                    final_grade
                )
                VALUES (?, ?, NULL, NULL, NULL, NULL)
            """, (
                student_id,
                course_id
            ))

            conn.commit()

            flash(
                "Student enrolled successfully.",
                "success"
            )

        except sqlite3.IntegrityError:

            flash(
                "This student has already enrolled in this course.",
                "warning"
            )

        return redirect(
            url_for("admin.enrollment")
        )

    cursor.execute("""
        SELECT
            e.enrollment_id,
            s.student_id,
            s.name,
            c.course_name,
            i.name
        FROM enrollments e
        JOIN students s
            ON e.student_id = s.student_id
        JOIN courses c
            ON e.course_id = c.course_id
        JOIN instructors i
            ON e.instructor_id = i.instructor_id
    """)

    enrollments = cursor.fetchall()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()

    cursor.execute("SELECT * FROM instructors")
    instructors = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_page/manage_enroll.html",
        students=students,
        courses=courses,
        instructors=instructors,
        enrollments=enrollments
    )

# --------------------------------------------
# Student Gradebook for managing student grade
# --------------------------------------------
@admin_bp.route("/gradebook", methods=["GET","POST"])
@login_required
@admin_required
def gradebook():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if request.method == "POST":

        student_id = request.form["student_id"]
        course_id = request.form["course_id"]

        assignment = float(request.form["assignment"])
        midterm = float(request.form["midterm"])
        final = float(request.form["final"])

        # -------------------------------
        # Find instructor for this student/course
        # -------------------------------
        cursor.execute("""
            SELECT instructor_id
            FROM enrollments
            WHERE student_id = ?
            AND course_id = ?
        """, (student_id, course_id))

        instructor = cursor.fetchone()

        if instructor is None:
            conn.close()
            return "This student is not enrolled in this course."

        instructor_id = instructor[0]

        # -------------------------------
        # Read grading weights
        # -------------------------------
        cursor.execute("""
            SELECT
                assignment_weight,
                midterm_weight,
                final_weight
            FROM grading_scheme
            WHERE course_id = ?
            AND instructor_id = ?
        """, (course_id, instructor_id))

        weights = cursor.fetchone()

        if weights is None:
            conn.close()
            return "This instructor has not set a grading scheme."

        grading = WeightedGrading(
            assignment,
            midterm,
            final,
            weights[0],
            weights[1],
            weights[2]
        )

        final_grade = grading.calculate_grade()

            # Check if ID of student and course exist
        cursor.execute(
                """
                SELECT grade_id

                FROM grades

                WHERE student_id = ?
                AND course_id = ?
                """,
                (
                    student_id,
                    course_id
                )
            )
        existing = cursor.fetchone()

        if existing:

                cursor.execute(
                    """
                    UPDATE grades

                    SET
                        assignment = ?,
                        midterm = ?,
                        final = ?,
                        final_grade = ?

                    WHERE
                        student_id = ?
                    AND
                        course_id = ?
                    """,
                    (
                        assignment,
                        midterm,
                        final,
                        final_grade,
                        student_id,
                        course_id
                    )
                )
        else:            
                cursor.execute("""
                INSERT INTO grades
                (
                    student_id,
                    course_id,
                    assignment,
                    midterm,
                    final,
                    final_grade
                )
                VALUES (?,?,?,?,?,?)
                """,
                (
                    student_id,
                    course_id,
                    assignment,
                    midterm,
                    final,
                    final_grade
                ))

                conn.commit()

    cursor.execute("""
    SELECT
        g.grade_id,
        s.student_id,
        s.name,
        c.course_name,
        g.assignment,
        g.midterm,
        g.final,
        g.final_grade,
        CASE
            WHEN g.final_grade >= 60 THEN 'Pass'
            ELSE 'Fail'
        END AS status
    FROM grades g
    JOIN students s
        ON g.student_id=s.student_id
    JOIN courses c
        ON g.course_id=c.course_id
    """)

    grades = cursor.fetchall()

    cursor.execute(
        "SELECT * FROM students"
    )

    students = cursor.fetchall()

    cursor.execute(
        "SELECT * FROM courses"
    )

    courses = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_page/gradebook.html",
        students=students,
        courses=courses,
        grades=grades
    )


# ------------------------------------
# CSV/JSON Import and Export Functions
# ------------------------------------
UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)



# ------------------------------------

@admin_bp.route("/io")
@login_required
@admin_required
def io_page():

    return render_template(
        "admin_page/manage_inout.html",
        imported=0,
        updated=0,
        skipped=0,
        errors=[]
    )
    


# ------------------------------------

@admin_bp.route(
    "/import_csv",
    methods=["POST"]
)
@login_required
@admin_required
def import_csv():

    uploaded_files = request.files.getlist(
        "csv_files"
    )

    saved_files = []

    for file in uploaded_files:

        path = os.path.join(
            UPLOAD_FOLDER,
            file.filename
        )

        file.save(path)

        saved_files.append(path)

    result = import_multiple_csv(
    saved_files
)

    return render_template(
    "admin_page/manage_inout.html",

    imported=result["imported"],

    updated=result["updated"],

    skipped=result["skipped"],

    errors=result["errors"]
)


# ------------------------------------

@admin_bp.route("/export_json")
@login_required
@admin_required
def export_json():

    filename = export_report_json()

    return send_file(
        filename,
        as_attachment=True,
        download_name="grade_report.json",
        mimetype="application/json"
    )

# --------------------
# Attendance check API
# --------------------


# ------------------------------------
@admin_bp.route("/attendance")
@login_required
@admin_required
def attendance():

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            course_id,
            course_name,
            semester,
            sessions
        FROM courses
        ORDER BY semester, course_name
    """)

    courses = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_page/attendance.html",
        courses=courses
    )

@admin_bp.route("/attendance/<course_id>")
@login_required
@admin_required
def attendance_course(course_id):

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

    SELECT *

    FROM courses

    WHERE course_id=?

    """,(course_id,))

    course = cursor.fetchone()

    conn.close()

    return render_template(

        "admin_page/attendance_course.html",

        course=course,

        sessions=range(
            1,
            course["sessions"]+1
        )

    )

@admin_bp.route(
"/attendance/<course_id>/<int:session_number>"
)
@login_required
@admin_required
def attendance_session(course_id,session_number):

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

    SELECT

        s.student_id,

        s.name,

        ar.status

    FROM enrollments e

    JOIN students s

        ON s.student_id=e.student_id

    LEFT JOIN attendance_records ar

        ON ar.student_id=e.student_id

        AND ar.course_id=e.course_id

        AND ar.session_number=?

    WHERE e.course_id=?

    ORDER BY s.name

    """,

    (

        session_number,

        course_id

    ))

    students = cursor.fetchall()

    conn.close()

    return render_template(

        "admin_page/attendance_session.html",

        students=students,

        session_number=session_number,

        course_id=course_id

    )


@admin_bp.route(
"/attendance/save",
methods=["POST"]
)
@login_required
@admin_required
def attendance_save():

    course_id=request.form["course_id"]

    session_number=int(
        request.form["session_number"]
    )

    today=date.today()

    student_ids=request.form.getlist("student_id")

    statuses=request.form.getlist("status")

    conn=sqlite3.connect(DATABASE)

    cursor=conn.cursor()

    for student,status in zip(student_ids,statuses):

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

            student,

            course_id,

            session_number,

            today,

            status

        ))

    conn.commit()

    conn.close()

    update_attendance_rate(course_id)

    return redirect(

        url_for(

            "admin.attendance_session",

            course_id=course_id,

            session_number=session_number

        )

    )
@admin_bp.route("/attendance/report")
@login_required
@admin_required
def attendance_report():

    conn=sqlite3.connect(DATABASE)

    query="""

    SELECT

        s.student_id,

        s.name,

        c.course_name,

        a.attendance_rate

    FROM attendance a

    JOIN students s

        ON a.student_id=s.student_id

    JOIN courses c

        ON a.course_id=c.course_id

    ORDER BY

        c.course_name,

        s.name

    """

    df=pd.read_sql_query(query,conn)

    conn.close()

    return render_template(

        "admin_page/attendance_report.html",

        table=df.to_html(
            classes="table table-striped",
            index=False
        )

    )
# -------------------------
# Pandas Analysis Functions
# -------------------------

@admin_bp.route("/pdanalytics")
@login_required
@admin_required
def pdanalytics():

    return render_template(
        "admin_page/pdanalytics.html"
    )


# ------------------------------------

@admin_bp.route("/analytics/gpa")
@login_required
@admin_required
def analytics_gpa():

    df = calculate_gpa()

    return df.to_html(
        classes="table table-striped",
        index=False
    )

# ------------------------------------

@admin_bp.route(
    "/analytics/ranking/<semester>"
)
@login_required
@admin_required
def analytics_ranking(semester):

    df = class_ranking(
        semester
    )

    return df.to_html(
        classes="table table-striped",
        index=False
    )


    

# ---------------------------------
@admin_bp.route("/report_gd/grade_distribution")
@login_required
@admin_required
def report_grade_distribution():


    return grade_distribution()

# ------------------------------------

@admin_bp.route(
    "/report_gpa/gpa_trend/<student_id>"
)
@login_required
@admin_required
def report_gpa_trend(
    student_id
):

    gpa_trend(
        student_id
    )

    return send_file(
        f"report_gpa/gpa_trend_{student_id}.png"
    )

# ------------------------------------

@admin_bp.route(
    "/report_cd/course_difficulty"
)
@login_required
@admin_required
def report_course_difficulty():

    return course_difficulty()



# ------------------------------------

@admin_bp.route(
    "/report_r/radar/<student_id>"
)
@login_required
@admin_required
def report_radar(
    student_id
):

    performance_radar(
        student_id
    )

    return send_file(
        f"report_r/radar_{student_id}.png"
    )

@admin_bp.route("/matplotlibvisual")
@login_required
@admin_required
def matplotlibvisual():

    return render_template(
        "admin_page/matplotlibvisual.html")
