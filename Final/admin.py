from BaseClasses import Student, Instructor, Course, WeightedGrading
from pd_analytics import calculate_gpa, class_ranking, attendance_grade_correlation, midterm_final_correlation
from matplotlib_charts import grade_distribution, gpa_trend,course_difficulty,performance_radar
from attendancemark import mark_attendance, DB_NAME
import pandas as pd
from flask import Flask, Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import send_file
import sqlite3
import os
from create_table import create_database, DATABASE
from CSV_JSON import (import_multiple_csv, export_report_json)

admin_bp = Blueprint("admin", __name__)


# -------------------------
# Loading UI/UX Function
# ------------------------
@admin_bp.route("/admin")
def home():
    return render_template("admin.html")

# ----------------------------------------------------------
# Add and Store Student Information (ID, Name, Email, Major)
# ----------------------------------------------------------

@admin_bp.route("/student", methods=["GET","POST"])
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
        "student.html",
        students=students
    )

# ------------------------------------------------------------------
# Add and Store Instructor Information (ID, Name, Email, Department)
# ------------------------------------------------------------------

@admin_bp.route("/instructor", methods=["GET","POST"])
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

    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM instructors
    """)

    instructors = cursor.fetchall()

    conn.close()

    return render_template(
        "instructor.html",
        instructors=instructors
    )

# ----------------------------------------------------------------------------------
# Add and Store Course Information (ID, Name, Credits, Semester, Number of Sessions)
# ----------------------------------------------------------------------------------

@admin_bp.route("/course", methods=["GET","POST"])
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
                    "course.html",
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
        "course.html",
        courses=courses
    )


# ---------------------------------------------
# Manage data between student, course, and instructor
# ---------------------------------------------

@admin_bp.route("/enrollment", methods=["GET","POST"])
def enrollment():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if request.method == "POST":

        student_id = request.form["student_id"]
        course_id = request.form["course_id"]
        instructor_id = request.form["instructor_id"]
        cursor.execute("""
        INSERT INTO enrollments
        (student_id,course_id,instructor_id)
        VALUES (?,?,?)
        """,(student_id,course_id,instructor_id))

        conn.commit()

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
        "enrollment.html",
        students=students,
        courses=courses,
        instructors=instructors,
        enrollments=enrollments
    )

# --------------------------------------------
# Student Gradebook for managing student grade
# --------------------------------------------
@admin_bp.route("/gradebook", methods=["GET","POST"])
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
        "gradebook.html",
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
def io_page():

    return render_template(
        "io.html",
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
    "io.html",

    imported=result["imported"],

    updated=result["updated"],

    skipped=result["skipped"],

    errors=result["errors"]
)


# ------------------------------------

@admin_bp.route("/export_json")
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

@admin_bp.route("/attendance")
def attendance_page():

    return render_template(
        "attendance.html"
    )

# ------------------------------------

@admin_bp.route(
    "/attendance/mark",
    methods=["POST"]
)
def attendance_mark():

    student_id = request.form[
        "student_id"
    ]

    course_id = request.form[
        "course_id"
    ]

    session_number = int(
        request.form[
            "session_number"
        ]
    )

    status = request.form[
        "status"
    ]

    mark_attendance(
        student_id,
        course_id,
        session_number,
        status
    )

    return render_template(
        "attendance.html",
        message=
        "Attendance recorded successfully."
    )

# ------------------------------------

@admin_bp.route("/attendance/report")
def attendance_report_route():

    conn = sqlite3.connect(
        DB_NAME
    )

    query = """
    SELECT

        ar.student_id,

        s.name,

        ar.course_id,

        c.course_name,

        ROUND(
            (
                COUNT(
                    CASE
                        WHEN ar.status='Present'
                        THEN 1
                    END
                ) * 100.0
            ) / c.sessions,
            2
        ) AS attendance_rate

    FROM attendance_records ar

    JOIN students s

        ON ar.student_id=s.student_id

    JOIN courses c

        ON ar.course_id=c.course_id

    GROUP BY

        ar.student_id,
        ar.course_id
    """

    df = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    return df.to_html(
        classes="table",
        index=False
    )


# -------------------------
# Pandas Analysis Functions
# -------------------------

@admin_bp.route("/pdanalytics")
def pdanalytics():

    return render_template(
        "pdanalytics.html"
    )


# ------------------------------------

@admin_bp.route("/analytics/gpa")
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
def analytics_ranking(semester):

    df = class_ranking(
        semester
    )

    return df.to_html(
        classes="table table-striped",
        index=False
    )



# ------------------------------------


@admin_bp.route(
    "/analytics/attendance_grade"
)
def attendance_grade_corr_route():

    corr = attendance_grade_correlation()

    return render_template(
        "attendance.html",
        attendance_corr=
        round(corr,4)
    )


# ------------------------------------


@admin_bp.route(
    "/analytics/midterm_final"
)
def midterm_final_corr_route():

    corr = midterm_final_correlation()

    return render_template(
        "attendance.html",
        midterm_corr=
        round(corr,4)
    )
    

# ---------------------------------
@admin_bp.route("/report_gd/grade_distribution")
def report_grade_distribution():


    return grade_distribution()

# ------------------------------------

@admin_bp.route(
    "/report_gpa/gpa_trend/<student_id>"
)
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
def report_course_difficulty():

    return course_difficulty()



# ------------------------------------

@admin_bp.route(
    "/report_r/radar/<student_id>"
)
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
def matplotlibvisual():

    return render_template(
        "matplotlibvisual.html")
