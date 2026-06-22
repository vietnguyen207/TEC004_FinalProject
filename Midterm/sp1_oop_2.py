"""
SP1 - OOP Grade Management System
University Course Performance Tracker & Grade Prediction System
TEC004/05

Hierarchy:
  Person (abstract)
    ├── Student
    └── Instructor

  Course (with enrollment management)
  GradeBook (polymorphic grading schemes: Weighted, Curved, PassFail)
"""

from abc import ABC, abstractmethod
from datetime import date
from functools import reduce
from typing import Optional


# ─────────────────────────────────────────────
# Abstract Base Class
# ─────────────────────────────────────────────

class Person(ABC):
    """Abstract base class for all persons in the system."""

    def __init__(self, person_id: str, name: str, email: str, dob: date):
        self._person_id = person_id
        self._name = name
        self._email = email
        self._dob = dob

    # Properties (encapsulation)
    @property
    def person_id(self): return self._person_id

    @property
    def name(self): return self._name

    @property
    def email(self): return self._email

    @abstractmethod
    def get_role(self) -> str:
        """Each subclass must declare its role."""
        pass

    @abstractmethod
    def summary(self) -> str:
        """Return a human-readable summary."""
        pass

    def __repr__(self):
        return f"<{self.get_role()} id={self._person_id} name={self._name}>"


# ─────────────────────────────────────────────
# Student
# ─────────────────────────────────────────────

class Student(Person):
    def __init__(self, person_id: str, name: str, email: str,
                 dob: date, major: str, year: int):
        super().__init__(person_id, name, email, dob)
        self.major = major
        self.year = year                    # 1=Freshman … 4=Senior
        self._enrolled_courses: list[str] = []  # list of course_ids

    def get_role(self) -> str:
        return "Student"

    def enroll(self, course_id: str):
        if course_id not in self._enrolled_courses:
            self._enrolled_courses.append(course_id)

    def drop(self, course_id: str):
        self._enrolled_courses = [c for c in self._enrolled_courses
                                  if c != course_id]

    @property
    def enrolled_courses(self):
        return list(self._enrolled_courses)

    def summary(self) -> str:
        return (f"Student | {self._name} | {self.major} Year-{self.year} "
                f"| Courses: {len(self._enrolled_courses)}")


# ─────────────────────────────────────────────
# Instructor
# ─────────────────────────────────────────────

class Instructor(Person):
    def __init__(self, person_id: str, name: str, email: str,
                 dob: date, department: str, title: str = "Lecturer"):
        super().__init__(person_id, name, email, dob)
        self.department = department
        self.title = title
        self._courses_taught: list[str] = []

    def get_role(self) -> str:
        return "Instructor"

    def assign_course(self, course_id: str):
        if course_id not in self._courses_taught:
            self._courses_taught.append(course_id)

    @property
    def courses_taught(self):
        return list(self._courses_taught)

    def summary(self) -> str:
        return (f"Instructor | {self.title} {self._name} | {self.department} "
                f"| Teaches: {len(self._courses_taught)} course(s)")


# ─────────────────────────────────────────────
# Course
# ─────────────────────────────────────────────

class Course:
    """Manages a university course and its enrolled students."""

    MAX_CAPACITY = 50

    def __init__(self, course_id: str, title: str,
                 instructor: Instructor, credits: int = 3):
        self.course_id = course_id
        self.title = title
        self.instructor = instructor
        self.credits = credits
        self._students: dict[str, Student] = {}   # student_id -> Student
        instructor.assign_course(course_id)

    # ── Enrollment management ──────────────────

    def enroll_student(self, student: Student) -> bool:
        if len(self._students) >= self.MAX_CAPACITY:
            print(f"[Course] {self.title} is full ({self.MAX_CAPACITY} seats).")
            return False
        if student.person_id in self._students:
            print(f"[Course] {student.name} is already enrolled.")
            return False
        self._students[student.person_id] = student
        student.enroll(self.course_id)
        print(f"[Course] {student.name} enrolled in '{self.title}'.")
        return True

    def drop_student(self, student: Student) -> bool:
        if student.person_id not in self._students:
            print(f"[Course] {student.name} is not enrolled.")
            return False
        del self._students[student.person_id]
        student.drop(self.course_id)
        print(f"[Course] {student.name} dropped from '{self.title}'.")
        return True

    @property
    def enrolled_count(self):
        return len(self._students)

    @property
    def roster(self) -> list[Student]:
        return list(self._students.values())

    def __repr__(self):
        return (f"<Course {self.course_id}: '{self.title}' "
                f"| {self.enrolled_count} students>")


# ─────────────────────────────────────────────
# GradeBook – base & polymorphic subclasses
# ─────────────────────────────────────────────

class GradeBook(ABC):
    """
    Abstract GradeBook. Subclasses implement calculate_grade()
    to support different grading schemes.
    """

    def __init__(self, course: Course):
        self.course = course
        # { student_id: {"midterm": float, "final": float,
        #                 "assignments": [float,...], "attendance": float} }
        self._records: dict[str, dict] = {}

    # ── Record management ──────────────────────

    def add_record(self, student: Student,
                   midterm: float = 0.0,
                   final: float = 0.0,
                   assignments: Optional[list[float]] = None,
                   attendance: float = 100.0):
        if student.person_id not in [s.person_id for s in self.course.roster]:
            raise ValueError(f"{student.name} is not enrolled in {self.course.title}.")
        self._records[student.person_id] = {
            "name": student.name,
            "midterm": midterm,
            "final": final,
            "assignments": assignments or [],
            "attendance": attendance,
        }

    def get_record(self, student_id: str) -> dict:
        return self._records.get(student_id, {})

    # ── Abstract method – override per scheme ──

    @abstractmethod
    def calculate_grade(self, student_id: str) -> float:
        """Return the final numeric grade (0–100) for a student."""
        pass

    def letter_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90: return "A"
        if score >= 80: return "B"
        if score >= 70: return "C"
        if score >= 60: return "D"
        return "F"

    def class_summary(self) -> dict:
        """Return basic stats for the whole class."""
        grades = [self.calculate_grade(sid) for sid in self._records]
        if not grades:
            return {}
        avg = sum(grades) / len(grades)
        return {
            "count": len(grades),
            "average": round(avg, 2),
            "highest": round(max(grades), 2),
            "lowest": round(min(grades), 2),
            "pass_rate": round(sum(1 for g in grades if g >= 60) / len(grades) * 100, 1),
        }

    def print_report(self):
        print(f"\n{'='*55}")
        print(f"  GradeBook: {self.course.title} [{type(self).__name__}]")
        print(f"{'='*55}")
        for sid, rec in self._records.items():
            score = self.calculate_grade(sid)
            print(f"  {rec['name']:<25} {score:6.2f}  {self.letter_grade(score)}")
        stats = self.class_summary()
        print(f"{'─'*55}")
        print(f"  Class avg: {stats.get('average', 'N/A')}  "
              f"Pass rate: {stats.get('pass_rate', 'N/A')}%")
        print(f"{'='*55}\n")


# ── Scheme 1: Weighted ─────────────────────────

class WeightedGradeBook(GradeBook):
    """
    Grade = midterm*30% + final*40% + assignments_avg*20% + attendance*10%
    """
    WEIGHTS = {"midterm": 0.30, "final": 0.40,
               "assignments": 0.20, "attendance": 0.10}

    def calculate_grade(self, student_id: str) -> float:
        rec = self._records.get(student_id)
        if not rec:
            return 0.0
        asgn_avg = (sum(rec["assignments"]) / len(rec["assignments"])
                    if rec["assignments"] else 0.0)
        score = (rec["midterm"]   * self.WEIGHTS["midterm"] +
                 rec["final"]     * self.WEIGHTS["final"] +
                 asgn_avg         * self.WEIGHTS["assignments"] +
                 rec["attendance"]* self.WEIGHTS["attendance"])
        return round(score, 2)


# ── Scheme 2: Curved ───────────────────────────

class CurvedGradeBook(GradeBook):
    """
    Raw grade = midterm*40% + final*60%.
    A curve is added so the class average reaches `target_avg`.
    """
    def __init__(self, course: Course, target_avg: float = 75.0):
        super().__init__(course)
        self.target_avg = target_avg

    def _raw_grade(self, student_id: str) -> float:
        rec = self._records.get(student_id)
        if not rec:
            return 0.0
        return round(rec["midterm"] * 0.40 + rec["final"] * 0.60, 2)

    def _curve_delta(self) -> float:
        raws = [self._raw_grade(sid) for sid in self._records]
        if not raws:
            return 0.0
        return max(0.0, self.target_avg - (sum(raws) / len(raws)))

    def calculate_grade(self, student_id: str) -> float:
        return min(100.0, round(self._raw_grade(student_id) + self._curve_delta(), 2))


# ── Scheme 3: Pass/Fail ────────────────────────

class PassFailGradeBook(GradeBook):
    """
    Students receive Pass (≥ threshold) or Fail (< threshold).
    calculate_grade() returns 100 for pass, 0 for fail.
    """
    def __init__(self, course: Course, threshold: float = 60.0):
        super().__init__(course)
        self.threshold = threshold

    def calculate_grade(self, student_id: str) -> float:
        rec = self._records.get(student_id)
        if not rec:
            return 0.0
        raw = rec["midterm"] * 0.50 + rec["final"] * 0.50
        return 100.0 if raw >= self.threshold else 0.0

    def letter_grade(self, score: float) -> str:
        return "Pass" if score >= 60 else "Fail"


# ─────────────────────────────────────────────
# Quick demo / smoke-test
# ─────────────────────────────────────────────

if __name__ == "__main__":
    from datetime import date

    # --- People ---
    prof = Instructor("I001", "Dr. Smith", "smith@uni.edu",
                      date(1975, 6, 1), "Computer Science", "Professor")

    students = [
        Student("S001", "Alice Johnson", "alice@uni.edu", date(2002, 3, 10), "CS", 2),
        Student("S002", "Bob Martinez",  "bob@uni.edu",   date(2001, 7, 22), "CS", 3),
        Student("S003", "Carol Lee",     "carol@uni.edu", date(2003, 1, 5),  "CS", 1),
    ]

    # --- Course ---
    cs101 = Course("CS101", "Introduction to Programming", prof, credits=3)
    for s in students:
        cs101.enroll_student(s)

    print(prof.summary())
    for s in students:
        print(s.summary())

    # --- WeightedGradeBook ---
    wb = WeightedGradeBook(cs101)
    wb.add_record(students[0], midterm=88, final=92,
                  assignments=[85, 90, 78, 95], attendance=95)
    wb.add_record(students[1], midterm=70, final=65,
                  assignments=[60, 72, 68], attendance=80)
    wb.add_record(students[2], midterm=55, final=50,
                  assignments=[58, 62], attendance=70)
    wb.print_report()

    # --- CurvedGradeBook ---
    cb = CurvedGradeBook(cs101, target_avg=75)
    cb.add_record(students[0], midterm=88, final=92)
    cb.add_record(students[1], midterm=70, final=65)
    cb.add_record(students[2], midterm=55, final=50)
    cb.print_report()

    # --- PassFailGradeBook ---
    pf = PassFailGradeBook(cs101, threshold=60)
    pf.add_record(students[0], midterm=88, final=92)
    pf.add_record(students[1], midterm=70, final=65)
    pf.add_record(students[2], midterm=55, final=50)
    pf.print_report()
