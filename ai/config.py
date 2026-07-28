import os

########################################################################
# BASE PATH
########################################################################

BASE_DIR = os.path.dirname(__file__)

########################################################################
# MODEL
########################################################################

MODEL_PATH = os.path.join(
    BASE_DIR,
    "grade_model.pkl"
)

DATASET_PATH = os.path.join(
    BASE_DIR,
    "training_dataset.csv"
)

########################################################################
# FEATURES
########################################################################

FEATURE_COLUMNS = [

    "assignment",

    "midterm",

    "attendance_rate",

    "completion_rate"

]

TARGET_COLUMN = "final_grade"

########################################################################
# TRAINING
########################################################################

TEST_SIZE = 0.2

RANDOM_STATE = 42

########################################################################
# RISK THRESHOLD
########################################################################

LOW_RISK = 80

MEDIUM_RISK = 60

HIGH_RISK = 40

########################################################################
# RISK LABEL
########################################################################

LOW_RISK_LABEL = "Low Risk"

MEDIUM_RISK_LABEL = "Medium Risk"

HIGH_RISK_LABEL = "High Risk"

CRITICAL_LABEL = "Critical"

########################################################################
# ALERT MESSAGE
########################################################################

LOW_ALERT = "✅ Student is performing well."

MEDIUM_ALERT = "🟡 Student should improve performance."

HIGH_ALERT = "🟠 Student is at risk of failing."

CRITICAL_ALERT = "🔴 Critical! Immediate attention required."

########################################################################
# RECOMMENDATION
########################################################################

LOW_RECOMMENDATION = (
    " Excellent performance. "
    " Maintain current study habits."
)

MEDIUM_RECOMMENDATION = (
    " Review weak topics and "
    " improve assignment quality."
)

HIGH_RECOMMENDATION = (
    " Attend every remaining class, "
    " complete all homework, "
    " meet instructor for consultation."
)

CRITICAL_RECOMMENDATION = (
    " Immediate academic intervention required. "
    " Contact instructor and advisor."
)