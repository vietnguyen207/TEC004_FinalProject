import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
from pd_analytics import calculate_gpa
import numpy as np
import os
from flask import send_file
DB_NAME = "database_fp.db"
def grade_distribution():

    conn = sqlite3.connect(DB_NAME)

    df = pd.read_sql_query(
        """
        SELECT final_grade
        FROM grades
        """,
        conn
    )

    conn.close()

    plt.figure(figsize=(8,5))

    plt.hist(
        df["final_grade"],
        bins=10
    )

    plt.title(
        "Grade Distribution"
    )

    plt.xlabel(
        "Final Grade"
    )

    plt.ylabel(
        "Students"
    )


    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    os.makedirs(
    os.path.join(BASE_DIR, "report_gd"),
    exist_ok=True
)

    file_path = os.path.join(
    BASE_DIR,
    "report_gd",
    "grade_distribution.png"
)

    plt.savefig(file_path)

    plt.close()

    return send_file(
    file_path,
    mimetype="image/png"
)
def gpa_trend(student_id):

    gpa_df = calculate_gpa()

    student = gpa_df[
        gpa_df["student_id"]
        ==
        student_id
    ]

    plt.figure(figsize=(8,5))

    plt.plot(
        student["semester"],
        student["gpa"],
        marker="o"
    )

    plt.title(
        f"GPA Trend - {student_id}"
    )

    plt.xlabel("Semester")
    plt.ylabel("GPA")
    os.makedirs("report_gpa", exist_ok=True)
    plt.savefig(
        f"report_gpa/gpa_trend_{student_id}.png"
    )

    plt.close()

def course_difficulty():

    conn = sqlite3.connect(DB_NAME)

    query = """
    SELECT

        c.course_name,

        AVG(
            g.final_grade
        ) AS avg_grade

    FROM grades g

    JOIN courses c

        ON g.course_id = c.course_id

    GROUP BY c.course_name
    """

    df = pd.read_sql_query(
        query,
        conn
    )

    conn.close()
    
    plt.figure(
        figsize=(10,5)
    )

    plt.bar(
        df["course_name"],
        df["avg_grade"]
    )

    plt.xticks(
        rotation=45
    )

    plt.title(
        "Course Difficulty Comparison"
    )

    plt.ylabel(
        "Average Grade"
    )
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    os.makedirs(
    os.path.join(BASE_DIR, "report_cd"),
    exist_ok=True
)

    file_path = os.path.join(
    BASE_DIR,
    "report_cd",
    "course_difficulty.png"
)

    plt.savefig(file_path)

    plt.close()

    return send_file(
    file_path,
    mimetype="image/png"
)
def performance_radar(student_id):

    conn = sqlite3.connect(DB_NAME)

    query = f"""
    SELECT

        AVG(assignment)
            as assignment,

        AVG(midterm)
            as midterm,

        AVG(final)
            as final_exam

    FROM grades

    WHERE student_id =
        '{student_id}'
    """

    df = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    values = [

        df["assignment"][0],
        df["midterm"][0],
        df["final_exam"][0]
    ]

    labels = [
        "Assignment",
        "Midterm",
        "Final"
    ]

    values += values[:1]

    angles = np.linspace(
        0,
        2*np.pi,
        len(labels),
        endpoint=False
    ).tolist()

    angles += angles[:1]

    plt.figure(
        figsize=(6,6)
    )

    ax = plt.subplot(
        polar=True
    )

    ax.plot(
        angles,
        values
    )

    ax.fill(
        angles,
        values,
        alpha=0.25
    )

    ax.set_xticks(
        angles[:-1]
    )

    ax.set_xticklabels(
        labels
    )

    plt.title(
        f"Performance Radar - {student_id}"
    )
    os.makedirs("report_r", exist_ok=True)
    plt.savefig(
        f"report_r/radar_{student_id}.png"
    )

    plt.close()