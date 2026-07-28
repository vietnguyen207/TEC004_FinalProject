import sqlite3
import pandas as pd

DATABASE = "database_fp.db"


def get_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


def load_grades(conn):

    query = """

        SELECT

            student_id,

            course_id,

            assignment,

            midterm,

            final_grade

        FROM grades

    """

    return pd.read_sql_query(query,conn)

def load_attendance(conn):

    query = """

        SELECT

            student_id,

            course_id,

            attendance_rate

        FROM attendance

    """

    return pd.read_sql_query(query,conn)


def load_total_assignments(conn):

    query = """

        SELECT

            course_id,

            COUNT(*) AS total_assignment

        FROM assignments

        WHERE assignment_type='assignment'

        GROUP BY course_id

    """

    return pd.read_sql_query(query, conn)

def load_completed_assignments(conn):

    query = """

        SELECT

            student_id,

            a.course_id,

            COUNT(DISTINCT a.assignment_id)

                AS completed_assignment

        FROM assignment_submissions s

        JOIN assignments a

        ON

            s.assignment_id=a.assignment_id

        WHERE

            s.status IN (

                'Submitted',

                'Graded'

            )

        AND

            a.assignment_type='assignment'

        GROUP BY

            student_id,

            a.course_id

    """

    return pd.read_sql_query(query, conn)

def load_enrollments(conn):

    query = """

        SELECT

            student_id,

            course_id

        FROM enrollments

    """

    return pd.read_sql_query(query, conn)

def calculate_completion_rate(conn):

    enrollments = load_enrollments(conn)

   
    total = load_total_assignments(conn)

   
    completed = load_completed_assignments(conn)

    # ---------------------------------------
    # Merge enrollments with completed assignments to get completed_assignment for each student-course pair
    # ---------------------------------------

    df = enrollments.merge(

        completed,

        on=[

            "student_id",

            "course_id"

        ],

        how="left"

    )

    # If a student has not completed any assignments, set completed_assignment to 0
    df["completed_assignment"] = df["completed_assignment"].fillna(0)

    # ---------------------------------------
    # Merge with total assignments to get total_assignment for each course
    # ---------------------------------------

    df = df.merge(

        total,

        on="course_id",

        how="left"

    )

    # If a course has no assignments, set total_assignment to 0
    df["total_assignment"] = df["total_assignment"].fillna(0)

    # ---------------------------------------
    # Calculate completion rate
    # ---------------------------------------

    df["completion_rate"] = 0.0

    mask = df["total_assignment"] > 0

    df.loc[mask, "completion_rate"] = (

        df.loc[mask, "completed_assignment"]

        /

        df.loc[mask, "total_assignment"]

    ) * 100

    df["completion_rate"] = df["completion_rate"].round(2)

    return df[
        [
            "student_id",
            "course_id",
            "completion_rate"
        ]
    ]

def build_dataset():

    conn = get_connection()

    # ----------------------------
    # Load dữ liệu
    # ----------------------------

    grades = load_grades(conn)

    attendance = load_attendance(conn)

    completion = calculate_completion_rate(conn)


    dataset = grades.merge(
        attendance,
        on=["student_id", "course_id"],
        how="left"
        )

    dataset["attendance_rate"] = dataset["attendance_rate"].fillna(0)



    dataset = dataset.merge(

        completion,

        on=[

            "student_id",

            "course_id"

        ],

        how="left"

    )
    dataset["completion_rate"] = dataset["completion_rate"].fillna(0)

    conn.close()

    return dataset


def clean_dataset(df):

    df=df.dropna(

        subset=[

            "assignment",

            "midterm",

            "attendance_rate",

            "completion_rate",

            "final_grade"

        ]

    )

    return df

def export_dataset(df):

    df.to_csv(

        "ai/training_dataset.csv",

        index=False

    )

    print(

        "Training dataset exported."

    )

if __name__=="__main__":

    df=build_dataset()

    df=clean_dataset(df)

    export_dataset(df)

    print(df.head())