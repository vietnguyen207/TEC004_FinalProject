from flask import Blueprint
from flask import render_template
from flask import session
from flask import redirect
from flask import url_for
from flask import request
from flask import flash
from ai.ai_service import (
    load_prediction_dataset,
    predict_student_service
)
from werkzeug.utils import secure_filename

from decorator import (
    login_required,
    student_required
)
import os
from student_logic import *

student_bp = Blueprint("student", __name__)

@student_bp.route("/student_db")
@login_required
@student_required
def dashboard():

    student = get_student_profile(
        session["user_id"]
    )

    return render_template(

        "student_page/dashboard.html",

        student=student

    )

@student_bp.route("/student_db/profile")
@login_required
@student_required
def profile():

    student = get_student_profile(
        session["user_id"]
    )

    return render_template(

        "student_page/profile.html",

        student=student

    )


@student_bp.route("/student_db/courses")
@login_required
@student_required
def my_courses():

    courses = get_my_courses(

        session["user_id"]

    )

    return render_template(

        "student_page/my_course.html",

        courses=courses

    )

@student_bp.route("/student_db/course/<course_id>")
@login_required
@student_required
def course_dashboard(course_id):

    if not student_owns_course(

        session["user_id"],

        course_id

    ):

        return "Permission Denied",403

    course = get_course(course_id)

    return render_template(

        "student_page/course_dashboard.html",

        course=course

    )


@student_bp.route(
"/student_db/course/<course_id>/attendance"
)
@login_required
@student_required
def attendance(course_id):

    student_id = session["user_id"]

    if not student_owns_course(student_id,course_id):

        return "Permission Denied",403

    course = get_course(course_id)

    attendance = get_my_attendance(

        student_id,

        course_id

    )

    rate = get_attendance_rate(

        student_id,

        course_id

    )

    return render_template(

        "student_page/attendance.html",

        course=course,

        attendance=attendance,

        rate=rate

    )


@student_bp.route(
"/student_db/course/<course_id>/attendance_report"
)
@login_required
@student_required
def attendance_report_page(course_id):

    student_id = session["user_id"]

    if not student_owns_course(student_id,course_id):

        return "Permission Denied",403

    course = get_course(course_id)

    report = attendance_report(

        student_id,

        course_id

    )

    rate = get_attendance_rate(

        student_id,

        course_id

    )
    summary = attendance_summary(

    student_id,

    course_id

)

    return render_template(

        "student_page/attendance_report.html",

        course=course,

        report=report,

        rate=rate,
        summary=summary

    )

@student_bp.route(
"/student_db/course/<course_id>/grades"
)
@login_required
@student_required
def grades(course_id):

    student_id = session["user_id"]

    if not student_owns_course(student_id,course_id):

        return "Permission Denied",403

    course = get_course(course_id)

    grades = get_my_grades(

        student_id,

        course_id

    )

    return render_template(

        "student_page/grade.html",

        course=course,

        grades=grades

    )

@student_bp.route(
"/student_db/course/<course_id>/grade_report"
)
@login_required
@student_required
def grade_report_page(course_id):

    student=session["user_id"]

    if not student_owns_course(
        student,
        course_id
    ):
        return "Permission Denied",403

    course=get_course(course_id)

    report=grade_report(
        student,
        course_id
    )

    homeworks=get_homework_scores(
        student,
        course_id
    )

    return render_template(

        "student_page/grade_report.html",

        course=course,

        report=report,

        homeworks=homeworks

    )

@student_bp.route("/student_db/gpa")
@login_required
@student_required
def gpa():

    student_id=session["user_id"]

    gpas=calculate_my_gpa(student_id)

    return render_template(

        "student_page/gpa.html",

        gpas=gpas

    )

@student_bp.route("/student_db/analytics")
@login_required
@student_required
def analytics():

    student_id=session["user_id"]

    gpa=calculate_my_gpa(student_id)

    attendance=get_attendance_statistics(student_id)

    grades=get_grade_statistics(student_id)

    return render_template(

        "student_page/analytics.html",

        gpa=gpa,

        attendance=attendance,

        grades=grades

    )

@student_bp.route(
"/student_db/course/<course_id>/assignments"
)
@login_required
@student_required
def assignments(course_id):
    student = session["user_id"]

    if not student_owns_course(student, course_id):
        return "Permission Denied", 403

    # Chỉ cần gọi 1 hàm duy nhất này (bỏ luôn vòng lặp submission_map):
    assignments = get_course_assignments(course_id, student)
    course = get_course(course_id)

    return render_template(
        "student_page/assignments.html",
        assignments=assignments,
        course=course
    )
@student_bp.route(

"/student_db/assignment/<int:assignment_id>/submit",

methods=["GET","POST"]

)
@login_required
@student_required
def submit_assignment_page(assignment_id):

    student=session["user_id"]

    submission=get_my_submission(
        student,
        assignment_id
    )
    
    if request.method=="POST":

        file=request.files["file"]

        filename=secure_filename(file.filename)

        assignment=get_assignment(assignment_id)

        folder=os.path.join(

            "uploads",

            "assignments",

            assignment["course_id"],

            str(assignment_id)

        )

        os.makedirs(folder,exist_ok=True)

        path=os.path.join(folder,filename)

        file.save(path)

        submit_assignment(

            assignment_id,

            student,

            filename,

            path

        )

        flash("Assignment submitted successfully!")

        return redirect(

            url_for(

                "student.assignments",

                course_id=assignment["course_id"]

            )

        )

    return render_template(

        "student_page/submit_assignment.html",

        submission=submission,
        assignment = get_assignment(assignment_id)
    )

@student_bp.route(
    "/student_db/course/<course_id>/prediction"
)
@login_required
@student_required
def prediction(course_id):

    student_id = session["user_id"]

    if not student_owns_course(student_id, course_id):
        return "Permission Denied", 403

    course = get_course(course_id)

    prediction_dataset = load_prediction_dataset()

    result = predict_student_service(

        prediction_dataset,

        student_id,

        course_id

    )

    return render_template(

        "student_page/prediction.html",

        course=course,

        result=result

    )