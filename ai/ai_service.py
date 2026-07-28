"""
Business Layer

Flask should only call this file.
"""

from ai.feature_builder import (
    get_connection,
    build_all_features,
    build_prediction_features
)

from ai.predict_engine import (
    predict_student,
    predict_course,
    predict_all_students,
    model_information
)

from ai.risk_engine import (
    calculate_risk,
    calculate_course_risk,
    build_dashboard,
    statistics,
    get_at_risk_students
)


########################################################################
# LOAD DATASET
########################################################################

def load_prediction_dataset():

    conn = get_connection()

    dataset = build_all_features(conn)

    prediction_dataset = build_prediction_features(dataset)

    conn.close()

    return prediction_dataset


########################################################################
# STUDENT
########################################################################

def predict_student_service(
        prediction_dataset,
        student_id,
        course_id
):

    prediction = predict_student(
        prediction_dataset,
        student_id,
        course_id
    )

    if prediction is None:
        return None

    result = calculate_risk(prediction)

    return result.to_dict()


########################################################################
# COURSE
########################################################################

def predict_course_service(
        prediction_dataset,
        course_id
):

    prediction = predict_course(

        prediction_dataset,

        course_id

    )

    return calculate_course_risk(
        prediction
    )


########################################################################
# DASHBOARD
########################################################################

def dashboard_service(
        prediction_dataset,
        course_id
):

    prediction = predict_course(

        prediction_dataset,

        course_id

    )

    return build_dashboard(
        prediction
    )


########################################################################
# STATISTICS
########################################################################

def dashboard_statistics_service(
        prediction_dataset,
        course_id
):

    prediction = predict_course(

        prediction_dataset,

        course_id

    )

    return statistics(
        prediction
    )


########################################################################
# AT RISK
########################################################################

def at_risk_students_service(
        prediction_dataset,
        course_id
):

    prediction = predict_course(

        prediction_dataset,

        course_id

    )

    return get_at_risk_students(
        prediction
    )


########################################################################
# SCHOOL
########################################################################

def predict_school_service(
        prediction_dataset
):

    prediction = predict_all_students(

        prediction_dataset

    )

    return calculate_course_risk(
        prediction
    )


########################################################################
# MODEL
########################################################################

def model_info_service():

    return model_information()