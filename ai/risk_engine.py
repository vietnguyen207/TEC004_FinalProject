import pandas as pd
from ai.config import (

    LOW_RISK,

    MEDIUM_RISK,

    HIGH_RISK,

    LOW_RISK_LABEL,

    MEDIUM_RISK_LABEL,

    HIGH_RISK_LABEL,

    CRITICAL_LABEL,

    LOW_ALERT,

    MEDIUM_ALERT,

    HIGH_ALERT,

    CRITICAL_ALERT,

    LOW_RECOMMENDATION,

    MEDIUM_RECOMMENDATION,

    HIGH_RECOMMENDATION,

    CRITICAL_RECOMMENDATION

)
########################################################################
# RISK LEVEL
########################################################################

def risk_level(predicted_grade):
    """
    Convert predicted grade to risk level.
    """

    if predicted_grade >= LOW_RISK:

        return LOW_RISK_LABEL

    elif predicted_grade >= MEDIUM_RISK:

        return MEDIUM_RISK_LABEL

    elif predicted_grade >= HIGH_RISK:

        return HIGH_RISK_LABEL


    else:

        return CRITICAL_LABEL


########################################################################
# RECOMMENDATION
########################################################################

def recommendation(predicted_grade):
    """
    Recommendation for student.
    """

    if predicted_grade >= 80:

        return LOW_RECOMMENDATION

    elif predicted_grade >= 60:

        return MEDIUM_RECOMMENDATION

    elif predicted_grade >= 40:

        return HIGH_RECOMMENDATION

    else:

        return CRITICAL_RECOMMENDATION


########################################################################
# ALERT MESSAGE
########################################################################

def generate_alert(predicted_grade):
    """
    Alert message.
    """

    if predicted_grade >= 80:

        return LOW_ALERT

    elif predicted_grade >= 60:

        return MEDIUM_ALERT

    elif predicted_grade >= 40:

        return HIGH_ALERT

    else:

        return CRITICAL_ALERT


########################################################################
# STUDENT RISK
########################################################################

def calculate_risk(student_prediction):
    """
    Add risk information for one student.
    """

    if student_prediction is None:

        return None

    result = student_prediction.copy()

    grade = float(result["predicted_final_grade"])

    result["risk_level"] = risk_level(grade)

    result["recommendation"] = recommendation(grade)

    result["alert"] = generate_alert(grade)

    return result


########################################################################
# COURSE RISK
########################################################################

def calculate_course_risk(course_prediction):
    """
    Add risk information for whole course.
    """

    if course_prediction is None:

        return pd.DataFrame()

    if course_prediction.empty:

        return pd.DataFrame()

    result = course_prediction.copy()

    result["risk_level"] = result[
        "predicted_final_grade"
    ].apply(risk_level)

    result["recommendation"] = result[
        "predicted_final_grade"
    ].apply(recommendation)

    result["alert"] = result[
        "predicted_final_grade"
    ].apply(generate_alert)

    return result


########################################################################
# DASHBOARD TABLE
########################################################################

def build_dashboard(course_prediction):
    """
    Data for Instructor Dashboard.
    """

    dashboard = calculate_course_risk(
        course_prediction
    )

    if dashboard.empty:

        return dashboard

    return dashboard[
        [

            "student_id",

            "predicted_final_grade",

            "risk_level",

            "alert"

        ]

    ]


########################################################################
# RISK STATISTICS
########################################################################

def statistics(course_prediction):
    """
    Count students in each risk level.
    """

    dashboard = calculate_course_risk(
        course_prediction
    )

    if dashboard.empty:

        return {}

    stat = dashboard[
        "risk_level"
    ].value_counts().to_dict()

    return stat


########################################################################
# FILTER AT RISK STUDENTS
########################################################################

def get_at_risk_students(course_prediction):
    """
    Return High Risk and Critical students.
    """

    dashboard = calculate_course_risk(
        course_prediction
    )

    if dashboard.empty:

        return dashboard

    return dashboard[

        dashboard["risk_level"].isin(

        [

            HIGH_RISK_LABEL,

            CRITICAL_LABEL

        ]

    )

    ]