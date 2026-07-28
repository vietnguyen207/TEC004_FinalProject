import os
import joblib
import numpy as np
import pandas as pd
from ai.feature_builder import *
from ai.config import (
    MODEL_PATH,
    FEATURE_COLUMNS
)

########################################################################
# LOAD MODEL
########################################################################

_model = None


def load_model():
    """
    Load trained model only once.
    """

    global _model

    if _model is None:

        _model = joblib.load(MODEL_PATH)

    return _model


########################################################################
# PREPARE FEATURE MATRIX
########################################################################

def prepare_features(df):
    """
    Keep only AI feature columns.
    """

    feature = df[FEATURE_COLUMNS].copy()

    feature = feature.fillna(0)

    feature = feature.astype(float)

    return feature


########################################################################
# PREDICT DATAFRAME
########################################################################

def predict_dataframe(df):
    """
    Predict every row in dataframe.
    """

    if df is None:

        return None

    if len(df) == 0:

        return None

    model = load_model()

    X = prepare_features(df)

    prediction = model.predict(X)

    result = df.copy()

    result["predicted_final_grade"] = np.round(
        prediction,
        2
    )

    return result


########################################################################
# PREDICT ONE STUDENT
########################################################################

def predict_student(
        prediction_dataset,
        student_id,
        course_id
):
    """
    Predict one student.
    """

    student = get_student_feature(prediction_dataset, student_id, course_id)

    if student.empty:

        return None

    result = predict_dataframe(student)

    return result.iloc[0]


########################################################################
# PREDICT WHOLE COURSE
########################################################################

def predict_course(
        prediction_dataset,
        course_id
):
    """
    Predict whole class.
    """

    course = get_course_feature(prediction_dataset, course_id)

    if course.empty:

        return pd.DataFrame()

    return predict_dataframe(course)


########################################################################
# PREDICT ALL STUDENTS
########################################################################

def predict_all_students(
        prediction_dataset
):
    """
    Predict every student.
    """

    return predict_dataframe(
        prediction_dataset
    )


########################################################################
# GET ONE PREDICTION VALUE
########################################################################

def get_prediction(
        prediction_dataset,
        student_id,
        course_id
):
    """
    Return only predicted grade.
    """

    result = predict_student(

        prediction_dataset,

        student_id,

        course_id

    )

    if result is None:

        return None

    return float(
        result["predicted_final_grade"]
    )


########################################################################
# GET COURSE PREDICTIONS
########################################################################

def get_course_predictions(
        prediction_dataset,
        course_id
):
    """
    Return simplified prediction table.
    """

    result = predict_course(

        prediction_dataset,

        course_id

    )

    if result.empty:

        return result

    return result[
        [

            "student_id",

            "predicted_final_grade"

        ]

    ]


########################################################################
# MODEL INFORMATION
########################################################################

def model_information():
    """
    Display model information.
    """

    model = load_model()

    info = {

        "model_type": type(model).__name__,

        "feature_columns": FEATURE_COLUMNS,

        "number_of_features": len(FEATURE_COLUMNS)

    }

    return info