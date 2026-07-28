import os
import sqlite3
import pandas as pd


# ==========================================
# PATH
# ==========================================

BASE_DIR = os.path.dirname(__file__)

DATABASE = os.path.join(

    BASE_DIR,

    "..",

    "database_fp.db"

)


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# ==========================================
# LOAD GRADE FEATURES
# ==========================================

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

    df = pd.read_sql_query(query, conn)

    return df


# ==========================================
# LOAD ATTENDANCE FEATURES
# ==========================================

def load_attendance(conn):

    query = """

        SELECT

            student_id,

            course_id,

            attendance_rate

        FROM attendance

    """

    df = pd.read_sql_query(query, conn)

    return df


# ==========================================
# LOAD ENROLLMENTS
# ==========================================

def load_enrollments(conn):

    query = """

        SELECT

            student_id,

            course_id

        FROM enrollments

    """

    df = pd.read_sql_query(query, conn)

    return df


# ==========================================
# TOTAL HOMEWORK OF EACH COURSE
# ==========================================

def load_total_assignments(conn):

    query = """

        SELECT

            course_id,

            COUNT(*) AS total_assignment

        FROM assignments

        WHERE

            assignment_type='assignment'

        GROUP BY

            course_id

    """

    df = pd.read_sql_query(query, conn)

    return df


# ==========================================
# COMPLETED HOMEWORK OF EACH STUDENT
# ==========================================

def load_completed_assignments(conn):

    query = """

        SELECT

            s.student_id,

            a.course_id,

            COUNT(

                DISTINCT

                s.assignment_id

            ) AS completed_assignment

        FROM assignment_submissions s

        JOIN assignments a

        ON

            s.assignment_id=a.assignment_id

        WHERE

            a.assignment_type='assignment'

        AND

            s.status IN(

                'Submitted',

                'Graded'

            )

        GROUP BY

            s.student_id,

            a.course_id

    """

    df = pd.read_sql_query(query, conn)

    return df

# ==========================================
# COMPLETION RATE
# ==========================================

def calculate_completion_rate(conn):

    enrollments = load_enrollments(conn)

    total = load_total_assignments(conn)

    completed = load_completed_assignments(conn)

    # Merge enrollment + completed homework

    df = enrollments.merge(

        completed,

        on=[

            "student_id",

            "course_id"

        ],

        how="left"

    )

    df["completed_assignment"] = df[

        "completed_assignment"

    ].fillna(0)

    # Merge total assignment

    df = df.merge(

        total,

        on="course_id",

        how="left"

    )

    df["total_assignment"] = df[

        "total_assignment"

    ].fillna(0)

    # Completion Rate

    df["completion_rate"] = 0.0

    mask = df["total_assignment"] > 0

    df.loc[mask, "completion_rate"] = (

        df.loc[mask, "completed_assignment"]

        /

        df.loc[mask, "total_assignment"]

    ) * 100

    df["completion_rate"] = df[

        "completion_rate"

    ].round(2)

    return df[
        [

            "student_id",

            "course_id",

            "completion_rate"

        ]

    ]
# ==========================================
# BUILD ALL FEATURES
# ==========================================

def build_all_features(conn):

    grades = load_grades(conn)

    attendance = load_attendance(conn)

    completion = calculate_completion_rate(conn)

    dataset = grades.merge(

        attendance,

        on=["student_id","course_id"],

        how="left"

    )

    dataset = dataset.merge(

        completion,

        on=["student_id","course_id"],

        how="left"

    )

    numeric = [

        "assignment",

        "midterm",

        "attendance_rate",

        "completion_rate",

        "final_grade"

    ]

    dataset[numeric] = dataset[numeric].fillna(0)

    dataset[numeric] = dataset[numeric].astype(float)

    return dataset
# ==========================================
# STUDENT FEATURE
# ==========================================

# ==========================================
# BUILD PREDICTION FEATURES
# ==========================================

def build_prediction_features(dataset):

    prediction = dataset[

        [

            "student_id",

            "course_id",

            "assignment",

            "midterm",

            "attendance_rate",

            "completion_rate"

        ]

    ].copy()

    numeric_columns = [

        "assignment",

        "midterm",

        "attendance_rate",

        "completion_rate"

    ]

    prediction[numeric_columns] = (

        prediction[numeric_columns]

        .fillna(0)

        .astype(float)

    )

    return prediction
# ==========================================
# GET STUDENT FEATURE
# ==========================================

def get_student_feature(

        prediction_dataset,

        student_id,

        course_id

):

    student = prediction_dataset[

        (prediction_dataset["student_id"] == student_id)

        &

        (prediction_dataset["course_id"] == course_id)

    ]

    if student.empty:

        return None

    return student[

        [

            "assignment",

            "midterm",

            "attendance_rate",

            "completion_rate"

        ]

    ]

# ==========================================
# GET COURSE FEATURE
# ==========================================

def get_course_feature(

        prediction_dataset,

        course_id

):

    course = prediction_dataset[

        prediction_dataset["course_id"] == course_id

    ]

    return course[
        [

            "student_id",

            "assignment",

            "midterm",

            "attendance_rate",

            "completion_rate"

        ]

    ]