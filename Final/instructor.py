from flask import Blueprint
from flask import render_template
from flask import session
from flask import abort
from flask import request
from flask import redirect
from flask import url_for
from decorator import login_required
from decorator import instructor_required

from instructor_logic import *

instructor_bp = Blueprint(
    "instructor",
    __name__
)

@instructor_bp.route("/instructor_db")
@login_required
@instructor_required
def dashboard():

    instructor_id = session["user_id"]

    courses = get_my_courses(instructor_id)

    total_course = len(courses)

    total_student = sum(
        c["total_students"]
        for c in courses
    )

    return render_template(

        "instructor_page/dashboard.html",

        instructor=session["username"],

        total_course=total_course,

        total_student=total_student,

        courses=courses

    )

@instructor_bp.route("/instructor_db/courses")
@login_required
@instructor_required
def my_courses():

    courses = get_my_courses(
        session["user_id"]
    )

    return render_template(

        "instructor_page/my_course.html",

        courses=courses

    )
@instructor_bp.route("/instructor/course/<course_id>")
@login_required
@instructor_required
def course_dashboard(course_id):

    course = get_course(course_id)

    return render_template(
        "instructor_page/course_dashboard.html",
        course=course
    )


@instructor_bp.route(
"/instructor/course/<course_id>/attendance"
)
@login_required
@instructor_required
def attendance_home(course_id):

    instructor_id = session["user_id"]

    if not instructor_owns_course(
        instructor_id,
        course_id
    ):
        abort(403)

    course = get_course(course_id)

    completed = get_session_status(course_id)

    return render_template(

        "instructor_page/attendance_home.html",

        course=course,

        completed=completed
    )

@instructor_bp.route(
    "/instructor/course/<course_id>/attendance/<int:session_number>",
    methods=["GET"]
)
@login_required
@instructor_required
def attendance(course_id, session_number):

    instructor_id = session["user_id"]

    # Kiểm tra instructor có dạy môn này không
    if not instructor_owns_course(instructor_id, course_id):
        abort(403)

    students = get_students(course_id)

    attendance = load_attendance(
        course_id,
        session_number
    )

    return render_template(
        "instructor_page/attendance.html",
        students=students,
        attendance=attendance,
        course_id=course_id,
        session_number=session_number
    )
@instructor_bp.route(
    "/instructor_db/course/<course_id>/attendance/save",
    methods=["POST"]
)
@login_required
@instructor_required
def attendance_save(course_id):

    session_number = request.form.get("session_number")

    if session_number is None:
        return "Session number is missing.", 400

    session_number = int(session_number)

    attendance_data = {}

    for key in request.form:

        if key.startswith("student_"):

            student_id = key.replace("student_", "")

            attendance_data[student_id] = request.form[key]

    save_attendance(
        course_id,
        session_number,
        attendance_data
    )

    update_attendance_rate(course_id)

    return redirect(
        url_for(
            "instructor.attendance",
            course_id=course_id,
            session_number=session_number
        )
    )

@instructor_bp.route(
    "/instructor_db/course/<course_id>/attendance/history"
)
@login_required
@instructor_required
def attendance_history(course_id):

    history=get_attendance_history(course_id)

    return render_template(

        "instructor_page/attendance_history.html",

        history=history,

        course_id=course_id
    )

@instructor_bp.route(
    "/instructor_db/course/<course_id>/attendance/report"
)
@login_required
@instructor_required
def attendance_report(course_id):

    report=attendance_report(course_id)

    return render_template(

        "instructor_page/attendance_report.html",

        report=report,

        course_id=course_id
    )


@instructor_bp.route("/course/<course_id>/grades")
@login_required
@instructor_required
def grades(course_id):

    course=get_course(course_id)

    grades=get_gradebook(course_id)

    return render_template(

        "instructor_page/gradebook.html",

        course=course,

        grades=grades
    )

@instructor_bp.route(

"/course/<course_id>/grades/edit/<student_id>",

methods=["GET","POST"]

)

@login_required
@instructor_required
def edit_grade(course_id,student_id):

    if request.method=="POST":

        assignment=float(request.form["assignment"])

        midterm=float(request.form["midterm"])

        final=float(request.form["final"])

        update_grade(

            student_id,

            course_id,

            assignment,

            midterm,

            final

        )

        return redirect(

            url_for(

                "instructor.grades",

                course_id=course_id

            )

        )

    grade=get_student_grade(student_id,course_id)

    return render_template(

        "instructor_page/edit_grade.html",

        grade=grade,

        course_id=course_id

    )

@instructor_bp.route(
"/course/<course_id>/grade_percentage",
methods=["GET","POST"]
)
@login_required
@instructor_required
def grade_percentage(course_id):

    if request.method=="POST":

        assignment=float(request.form["assignment_weight"])
        midterm=float(request.form["midterm_weight"])
        final=float(request.form["final_weight"])
        instructor_id = session["user_id"]
        if assignment+midterm+final !=100:

            weight=get_weight(course_id,instructor_id)

            return render_template(

                "instructor_page/grade_percentage.html",

                weight=weight,

                course_id=course_id,
                instructor_id=instructor_id,
                error="Total percentage must equal 100"

            )

        update_weight(

            course_id,

            instructor_id,

            assignment,

            midterm,

            final

        )

        return redirect(

            url_for(

                "instructor.course_dashboard",

                course_id=course_id

            )

        )

    weight=get_weight(course_id,instructor_id=session["user_id"])

    return render_template(

        "instructor_page/grade_percentage.html",

        weight=weight,

        course_id=course_id

    )


@instructor_bp.route(
"/course/<course_id>/calculate_final"
)
@login_required
@instructor_required
def calculate_final(course_id):

    calculate_final_grade(course_id)

    return redirect(

        url_for(

            "instructor.grades",

            course_id=course_id

        )

    )