"""
SP3 - SQLite Database Module
University Course Performance Tracker & Grade Prediction System
TEC004/05

Schema:
  Students    – student profiles
  Instructors – instructor profiles
  Courses     – course definitions
  Enrollments – student ↔ course (M:M) with foreign keys
  Grades      – per-student per-course scores
  Assignments – individual assignment submissions

Complex queries:
  - GPA calculation
  - Class rankings
  - At-risk student identification
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────
# Database Manager
# ─────────────────────────────────────────────

class DatabaseManager:
    """Handles connection, schema creation, and provides a context manager."""

    DDL = """
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS Instructors (
        instructor_id  TEXT PRIMARY KEY,
        name           TEXT NOT NULL,
        email          TEXT UNIQUE NOT NULL,
        department     TEXT,
        title          TEXT DEFAULT 'Lecturer'
    );

    CREATE TABLE IF NOT EXISTS Students (
        student_id  TEXT PRIMARY KEY,
        name        TEXT NOT NULL,
        email       TEXT UNIQUE NOT NULL,
        major       TEXT,
        year        INTEGER CHECK(year BETWEEN 1 AND 5)
    );

    CREATE TABLE IF NOT EXISTS Courses (
        course_id      TEXT PRIMARY KEY,
        title          TEXT NOT NULL,
        instructor_id  TEXT NOT NULL,
        credits        INTEGER DEFAULT 3,
        FOREIGN KEY (instructor_id) REFERENCES Instructors(instructor_id)
    );

    CREATE TABLE IF NOT EXISTS Enrollments (
        enrollment_id  INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id     TEXT NOT NULL,
        course_id      TEXT NOT NULL,
        semester       TEXT NOT NULL,
        UNIQUE (student_id, course_id, semester),
        FOREIGN KEY (student_id) REFERENCES Students(student_id),
        FOREIGN KEY (course_id)  REFERENCES Courses(course_id)
    );

    CREATE TABLE IF NOT EXISTS Grades (
        grade_id    INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id  TEXT NOT NULL,
        course_id   TEXT NOT NULL,
        midterm     REAL DEFAULT 0,
        final       REAL DEFAULT 0,
        attendance  REAL DEFAULT 100,
        final_grade REAL,               -- computed / stored
        letter      TEXT,
        UNIQUE (student_id, course_id),
        FOREIGN KEY (student_id) REFERENCES Students(student_id),
        FOREIGN KEY (course_id)  REFERENCES Courses(course_id)
    );

    CREATE TABLE IF NOT EXISTS Assignments (
        assignment_id  INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id     TEXT NOT NULL,
        course_id      TEXT NOT NULL,
        title          TEXT NOT NULL,
        score          REAL NOT NULL,
        max_score      REAL DEFAULT 100,
        submitted_at   TEXT,
        FOREIGN KEY (student_id) REFERENCES Students(student_id),
        FOREIGN KEY (course_id)  REFERENCES Courses(course_id)
    );
    """

    def __init__(self, db_path: str = "university.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with self.connect() as conn:
            conn.executescript(self.DDL)
        print(f"[DB] Initialised → {self.db_path}")

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row          # dict-like rows
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


# ─────────────────────────────────────────────
# Repository classes (CRUD)
# ─────────────────────────────────────────────

class StudentRepo:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def insert(self, student_id, name, email, major, year):
        with self.db.connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO Students VALUES (?,?,?,?,?)",
                (student_id, name, email, major, year)
            )

    def get(self, student_id) -> Optional[dict]:
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM Students WHERE student_id=?", (student_id,)
            ).fetchone()
            return dict(row) if row else None

    def all(self) -> list[dict]:
        with self.db.connect() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM Students")]

    def update(self, student_id, **kwargs):
        if not kwargs:
            return
        cols = ", ".join(f"{k}=?" for k in kwargs)
        with self.db.connect() as conn:
            conn.execute(
                f"UPDATE Students SET {cols} WHERE student_id=?",
                (*kwargs.values(), student_id)
            )

    def delete(self, student_id):
        with self.db.connect() as conn:
            conn.execute("DELETE FROM Students WHERE student_id=?", (student_id,))


class CourseRepo:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def insert(self, course_id, title, instructor_id, credits=3):
        with self.db.connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO Courses VALUES (?,?,?,?)",
                (course_id, title, instructor_id, credits)
            )

    def get(self, course_id) -> Optional[dict]:
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM Courses WHERE course_id=?", (course_id,)
            ).fetchone()
            return dict(row) if row else None


class EnrollmentRepo:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def enroll(self, student_id, course_id, semester="2024-S1"):
        with self.db.connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO Enrollments(student_id,course_id,semester) VALUES(?,?,?)",
                (student_id, course_id, semester)
            )

    def get_students(self, course_id) -> list[dict]:
        with self.db.connect() as conn:
            return [dict(r) for r in conn.execute(
                """SELECT s.* FROM Students s
                   JOIN Enrollments e ON s.student_id = e.student_id
                   WHERE e.course_id = ?""", (course_id,)
            )]


class GradeRepo:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def upsert(self, student_id, course_id, midterm, final,
               attendance, final_grade, letter):
        with self.db.connect() as conn:
            conn.execute("""
                INSERT INTO Grades(student_id,course_id,midterm,final,
                                   attendance,final_grade,letter)
                VALUES (?,?,?,?,?,?,?)
                ON CONFLICT(student_id,course_id) DO UPDATE SET
                    midterm=excluded.midterm,
                    final=excluded.final,
                    attendance=excluded.attendance,
                    final_grade=excluded.final_grade,
                    letter=excluded.letter
            """, (student_id, course_id, midterm, final,
                  attendance, final_grade, letter))

    def get_for_student(self, student_id) -> list[dict]:
        with self.db.connect() as conn:
            return [dict(r) for r in conn.execute(
                "SELECT * FROM Grades WHERE student_id=?", (student_id,)
            )]


class AssignmentRepo:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def insert(self, student_id, course_id, title, score,
               max_score=100, submitted_at=None):
        with self.db.connect() as conn:
            conn.execute(
                """INSERT INTO Assignments
                   (student_id,course_id,title,score,max_score,submitted_at)
                   VALUES (?,?,?,?,?,?)""",
                (student_id, course_id, title, score, max_score, submitted_at)
            )

    def avg_for_student_course(self, student_id, course_id) -> float:
        with self.db.connect() as conn:
            row = conn.execute("""
                SELECT AVG(score * 100.0 / max_score) as avg_pct
                FROM Assignments
                WHERE student_id=? AND course_id=?
            """, (student_id, course_id)).fetchone()
            return round(row["avg_pct"] or 0.0, 2)


# ─────────────────────────────────────────────
# Analytics Queries
# ─────────────────────────────────────────────

class Analytics:
    """
    Complex SQL queries for GPA, rankings, and at-risk detection.
    GPA uses a standard 4.0 scale based on letter grades.
    """

    GRADE_POINTS = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0}

    def __init__(self, db: DatabaseManager):
        self.db = db

    # ── GPA calculation ────────────────────────

    def student_gpa(self, student_id: str) -> float:
        """
        Weighted GPA = Σ(grade_points × credits) / Σ(credits)
        """
        with self.db.connect() as conn:
            rows = conn.execute("""
                SELECT g.letter, c.credits
                FROM Grades g
                JOIN Courses c ON g.course_id = c.course_id
                WHERE g.student_id = ?
            """, (student_id,)).fetchall()

        if not rows:
            return 0.0
        total_pts = sum(self.GRADE_POINTS.get(r["letter"], 0) * r["credits"]
                        for r in rows)
        total_cred = sum(r["credits"] for r in rows)
        return round(total_pts / total_cred, 3) if total_cred else 0.0

    def all_gpas(self) -> list[dict]:
        """GPA for every student."""
        with self.db.connect() as conn:
            students = [dict(r) for r in conn.execute("SELECT student_id, name FROM Students")]
        return sorted(
            [{"student_id": s["student_id"], "name": s["name"],
              "gpa": self.student_gpa(s["student_id"])} for s in students],
            key=lambda x: x["gpa"], reverse=True
        )

    # ── Class rankings ─────────────────────────

    def class_ranking(self, course_id: str) -> list[dict]:
        """
        Rank students in a course by final_grade (descending).
        Ties share the same rank.
        """
        with self.db.connect() as conn:
            rows = conn.execute("""
                SELECT s.student_id, s.name, g.final_grade, g.letter
                FROM Grades g
                JOIN Students s ON g.student_id = s.student_id
                WHERE g.course_id = ?
                ORDER BY g.final_grade DESC
            """, (course_id,)).fetchall()

        ranked = []
        prev_score, rank = None, 0
        for i, r in enumerate(rows):
            if r["final_grade"] != prev_score:
                rank = i + 1
                prev_score = r["final_grade"]
            ranked.append({
                "rank":        rank,
                "student_id":  r["student_id"],
                "name":        r["name"],
                "final_grade": r["final_grade"],
                "letter":      r["letter"],
            })
        return ranked

    # ── At-risk identification ─────────────────

    def at_risk_students(self,
                         min_grade: float = 60.0,
                         min_attendance: float = 75.0) -> list[dict]:
        """
        A student is at-risk if:
          - final_grade < min_grade  OR
          - attendance  < min_attendance
        Returns list with risk reason(s).
        """
        with self.db.connect() as conn:
            rows = conn.execute("""
                SELECT s.student_id, s.name, s.email,
                       g.course_id, g.final_grade, g.attendance, g.letter
                FROM Grades g
                JOIN Students s ON g.student_id = s.student_id
                WHERE g.final_grade < ? OR g.attendance < ?
                ORDER BY g.final_grade ASC
            """, (min_grade, min_attendance)).fetchall()

        results = []
        for r in rows:
            reasons = []
            if r["final_grade"] < min_grade:
                reasons.append(f"Low grade ({r['final_grade']:.1f})")
            if r["attendance"] < min_attendance:
                reasons.append(f"Low attendance ({r['attendance']:.1f}%)")
            results.append({**dict(r), "risk_reasons": ", ".join(reasons)})
        return results

    # ── Course stats ───────────────────────────

    def course_stats(self, course_id: str) -> dict:
        with self.db.connect() as conn:
            row = conn.execute("""
                SELECT COUNT(*) as n,
                       AVG(final_grade) as avg,
                       MAX(final_grade) as high,
                       MIN(final_grade) as low,
                       SUM(CASE WHEN final_grade >= 60 THEN 1 ELSE 0 END) as passed
                FROM Grades WHERE course_id = ?
            """, (course_id,)).fetchone()
            n = row["n"] or 0
        return {
            "course_id":  course_id,
            "count":      n,
            "average":    round(row["avg"] or 0, 2),
            "highest":    round(row["high"] or 0, 2),
            "lowest":     round(row["low"] or 0, 2),
            "pass_rate":  round((row["passed"] / n * 100) if n else 0, 1),
        }


# ─────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import os, tempfile

    db_file = tempfile.mktemp(suffix=".db")
    db   = DatabaseManager(db_file)

    # Repos
    s_repo  = StudentRepo(db)
    c_repo  = CourseRepo(db)
    e_repo  = EnrollmentRepo(db)
    g_repo  = GradeRepo(db)
    a_repo  = AssignmentRepo(db)
    analy   = Analytics(db)

    # Seed instructors
    with db.connect() as conn:
        conn.execute("INSERT OR IGNORE INTO Instructors VALUES (?,?,?,?,?)",
                     ("I001", "Dr. Smith", "smith@uni.edu", "CS", "Professor"))

    # Seed students
    students = [
        ("S001", "Alice Johnson", "alice@uni.edu", "CS", 2),
        ("S002", "Bob Martinez",  "bob@uni.edu",   "CS", 3),
        ("S003", "Carol Lee",     "carol@uni.edu", "CS", 1),
        ("S004", "David Kim",     "david@uni.edu", "Math", 2),
    ]
    for s in students:
        s_repo.insert(*s)

    # Seed courses
    c_repo.insert("CS101", "Intro to Programming", "I001", 3)
    c_repo.insert("CS102", "Data Structures",      "I001", 3)

    # Enroll
    for sid, *_ in students[:3]:
        e_repo.enroll(sid, "CS101")
    e_repo.enroll("S004", "CS102")
    e_repo.enroll("S001", "CS102")

    # Insert grades
    grade_data = [
        ("S001","CS101", 88, 92, 95, 90.4, "A"),
        ("S002","CS101", 70, 65, 80, 69.5, "D"),
        ("S003","CS101", 55, 50, 60, 53.5, "F"),
        ("S001","CS102", 90, 88, 98, 89.6, "B"),
        ("S004","CS102", 78, 74, 85, 75.8, "C"),
    ]
    for rec in grade_data:
        g_repo.upsert(*rec)

    # Insert assignments
    a_repo.insert("S001","CS101","HW1", 90)
    a_repo.insert("S001","CS101","HW2", 85)
    a_repo.insert("S002","CS101","HW1", 60)
    a_repo.insert("S003","CS101","HW1", 55)

    # ── Queries ────────────────────────────────
    print("\n=== GPA Ranking ===")
    for row in analy.all_gpas():
        print(f"  {row['name']:<20} GPA: {row['gpa']}")

    print("\n=== CS101 Class Ranking ===")
    for row in analy.class_ranking("CS101"):
        print(f"  #{row['rank']} {row['name']:<20} {row['final_grade']}  {row['letter']}")

    print("\n=== At-Risk Students ===")
    for row in analy.at_risk_students():
        print(f"  {row['name']:<20} [{row['course_id']}] {row['risk_reasons']}")

    print("\n=== CS101 Course Stats ===")
    print(" ", analy.course_stats("CS101"))

    os.unlink(db_file)
    print("\n[Demo] DB cleaned up.")
