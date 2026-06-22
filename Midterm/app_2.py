"""
app.py — Flask web server for University Grade Tracker
TEC004/05

Run:  python app.py
Open: http://127.0.0.1:5000
"""

from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import os, tempfile

from sp3_database import (
    DatabaseManager, StudentRepo, CourseRepo,
    EnrollmentRepo, GradeRepo, AssignmentRepo, Analytics
)
from sp2_fileio import CSVImporter
import pandas as pd

app = Flask(__name__)
CORS(app)

# ── Initialise DB ──────────────────────────────
db        = DatabaseManager("university.db")
s_repo    = StudentRepo(db)
c_repo    = CourseRepo(db)
e_repo    = EnrollmentRepo(db)
g_repo    = GradeRepo(db)
a_repo    = AssignmentRepo(db)
analytics = Analytics(db)


# ─────────────────────────────────────────────
# Pages
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ─────────────────────────────────────────────
# Students
# ─────────────────────────────────────────────

@app.route("/api/students", methods=["GET"])
def get_students():
    return jsonify(s_repo.all())


@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.json
    try:
        s_repo.insert(
            data["student_id"], data["name"],
            data["email"], data["major"], data["year"]
        )
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.route("/api/students/<student_id>", methods=["GET"])
def get_student(student_id):
    student = s_repo.get(student_id)
    if not student:
        return jsonify({"error": "Not found"}), 404
    return jsonify(student)


@app.route("/api/students/<student_id>", methods=["DELETE"])
def delete_student(student_id):
    try:
        s_repo.delete(student_id)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


# ─────────────────────────────────────────────
# Grades
# ─────────────────────────────────────────────

@app.route("/api/grades", methods=["GET"])
def get_grades():
    course = request.args.get("course")
    with db.connect() as conn:
        if course:
            rows = conn.execute(
                "SELECT * FROM Grades WHERE course_id = ?", (course,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM Grades").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/grades", methods=["POST"])
def add_grade():
    data = request.json
    try:
        mid  = float(data["midterm"])
        fin  = float(data["final"])
        att  = float(data["attendance"])
        asgn = 75.0  # default if no assignments provided

        # Weighted formula from SP1
        fg = round(mid * 0.30 + fin * 0.40 + asgn * 0.20 + att * 0.10, 2)

        def letter(s):
            if s >= 90: return "A"
            if s >= 80: return "B"
            if s >= 70: return "C"
            if s >= 60: return "D"
            return "F"

        g_repo.upsert(data["student_id"], data["course_id"],
                      mid, fin, att, fg, letter(fg))
        return jsonify({"ok": True, "final_grade": fg})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.route("/api/grades/<course_id>/ranking", methods=["GET"])
def grade_ranking(course_id):
    return jsonify(analytics.class_ranking(course_id))


# ─────────────────────────────────────────────
# At-risk
# ─────────────────────────────────────────────

@app.route("/api/at-risk", methods=["GET"])
def at_risk():
    min_grade = float(request.args.get("grade", 60))
    min_att   = float(request.args.get("attendance", 75))
    data = analytics.at_risk_students(min_grade, min_att)
    return jsonify(data)


# ─────────────────────────────────────────────
# Dashboard stats
# ─────────────────────────────────────────────

@app.route("/api/stats", methods=["GET"])
def stats():
    with db.connect() as conn:
        n_courses = conn.execute("SELECT COUNT(*) FROM Courses").fetchone()[0]
        total     = conn.execute("SELECT COUNT(*) FROM Grades").fetchone()[0]
        passed    = conn.execute(
            "SELECT COUNT(*) FROM Grades WHERE final_grade >= 60"
        ).fetchone()[0]
    pass_rate = round(passed / total * 100, 1) if total else 0
    return jsonify({"courses": n_courses, "pass_rate": pass_rate})


# ─────────────────────────────────────────────
# Analytics endpoints
# ─────────────────────────────────────────────

def _grades_df():
    """Load all grades into a DataFrame for SP4 analytics."""
    with db.connect() as conn:
        rows = conn.execute("""
            SELECT g.student_id, COALESCE(s.name,'') as name,
                   g.course_id, COALESCE(e.semester,'2024-S1') as semester,
                   g.midterm, g.final, g.attendance,
                   g.final_grade, 3 as credits
            FROM Grades g
            LEFT JOIN Students s    ON g.student_id = s.student_id
            LEFT JOIN Enrollments e ON g.student_id = e.student_id
                                    AND g.course_id = e.course_id
        """).fetchall()
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame([dict(r) for r in rows])


@app.route("/api/analytics/distribution", methods=["GET"])
def dist():
    df = _grades_df()
    if df.empty:
        return jsonify([])
    from sp4_analytics import GradeAnalytics
    engine = GradeAnalytics(df)
    course = request.args.get("course")
    result = engine.grade_distribution(course if course else None)
    return jsonify(result.to_dict(orient="records"))


@app.route("/api/analytics/passfail", methods=["GET"])
def passfail():
    df = _grades_df()
    if df.empty:
        return jsonify([])
    from sp4_analytics import GradeAnalytics
    engine = GradeAnalytics(df)
    result = engine.pass_fail_by_course()
    return jsonify(result.to_dict(orient="records"))


@app.route("/api/analytics/correlation", methods=["GET"])
def correlation():
    df = _grades_df()
    if df.empty:
        return jsonify({})
    from sp4_analytics import GradeAnalytics
    engine = GradeAnalytics(df)
    return jsonify({
        "attendance_grade": engine.attendance_grade_correlation(),
        "midterm_final":    engine.midterm_final_correlation(),
    })


@app.route("/api/analytics/difficulty", methods=["GET"])
def difficulty():
    df = _grades_df()
    if df.empty:
        return jsonify([])
    from sp4_analytics import GradeAnalytics
    engine = GradeAnalytics(df)
    result = engine.course_difficulty_comparison()
    return jsonify(result.to_dict(orient="records"))


@app.route("/api/analytics/gpa", methods=["GET"])
def gpa():
    return jsonify(analytics.all_gpas())


# ─────────────────────────────────────────────
# CSV Upload
# ─────────────────────────────────────────────

@app.route("/api/upload", methods=["POST"])
def upload_csv():
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "No file provided"}), 400
    f = request.files["file"]
    if not f.filename.endswith(".csv"):
        return jsonify({"ok": False, "error": "File must be a .csv"}), 400

    tmp = tempfile.mktemp(suffix=".csv")
    f.save(tmp)
    try:
        importer = CSVImporter(tmp)
        records  = importer.load()
        course_id = f.filename.split("_")[0].upper()

        def letter(s):
            if s >= 90: return "A"
            if s >= 80: return "B"
            if s >= 70: return "C"
            if s >= 60: return "D"
            return "F"

        imported = 0
        for rec in records:
            sid  = rec["student_id"]
            mid  = rec["midterm"]
            fin  = rec["final"]
            att  = rec["attendance"]
            asgn = sum(rec["assignments"]) / len(rec["assignments"]) if rec["assignments"] else 75.0
            fg   = round(mid * 0.30 + fin * 0.40 + asgn * 0.20 + att * 0.10, 2)

            # Auto-create student if not exists
            if not s_repo.get(sid):
                s_repo.insert(sid, rec["name"],
                              f"{sid.lower()}@uni.edu", "Unknown", 1)

            g_repo.upsert(sid, course_id, mid, fin, att, fg, letter(fg))
            imported += 1

        return jsonify({"ok": True, "rows": imported})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        os.unlink(tmp)


# ─────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)
