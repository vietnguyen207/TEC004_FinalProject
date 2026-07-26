import sqlite3
import pandas as pd

DB_NAME = "database_fp.db"

def get_grade_data():

    conn = sqlite3.connect(DB_NAME)

    query = """
    SELECT

        s.student_id,
        s.name,

        c.course_id,
        c.course_name,
        c.credits,
        c.semester,

        g.final_grade

    FROM grades g

    JOIN students s
        ON g.student_id = s.student_id

    JOIN courses c
        ON g.course_id = c.course_id
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df

def calculate_gpa():

    df = get_grade_data()

    df["weighted_grade"] = (
        df["final_grade"]
        * df["credits"]
    )

    gpa_df = (

        df.groupby(
            [
                "student_id",
                "name",
                "semester"
            ]
        )

        .agg(

            total_weighted_grade=
            ("weighted_grade", "sum"),

            total_credits=
            ("credits", "sum")

        )

        .reset_index()
    )

    gpa_df["gpa"] = (

        gpa_df["total_weighted_grade"]

        /

        gpa_df["total_credits"]

    )

    gpa_df["gpa"] = gpa_df["gpa"].round(2)

    return gpa_df


def class_ranking(semester):

    gpa_df = calculate_gpa()

    semester_df = gpa_df[
        gpa_df["semester"] == semester
    ]

    semester_df["rank"] = (
        semester_df["gpa"]
        .rank(
            ascending=False,
            method="dense"
        )
    )

    semester_df = semester_df.sort_values(
        "rank"
    )

    return semester_df

