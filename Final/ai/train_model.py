import os
import joblib
import pandas as pd

from sklearn.linear_model import LinearRegression

from sklearn.model_selection import train_test_split

from sklearn.metrics import (

    mean_absolute_error,

    mean_squared_error,

    r2_score

)


# ==========================================
# File Path
# ==========================================

BASE_DIR = os.path.dirname(__file__)

DATASET = os.path.join(

    BASE_DIR,

    "training_dataset.csv"

)

MODEL = os.path.join(

    BASE_DIR,

    "grade_model.pkl"

)

REPORT = os.path.join(

    BASE_DIR,

    "model_report.txt"

)

COEFFICIENT = os.path.join(

    BASE_DIR,

    "model_coefficients.csv"

)


# ==========================================
# Load Dataset
# ==========================================

def load_dataset():

    df = pd.read_csv(DATASET)

    return df


# ==========================================
# Prepare Features
# ==========================================

def prepare_data(df):

    X = df[

        [

            "assignment",

            "midterm",

            "attendance_rate",

            "completion_rate"

        ]

    ]

    y = df["final_grade"]

    return X, y


# ==========================================
# Split Dataset
# ==========================================

def split_dataset(X, y):

    return train_test_split(

        X,

        y,

        test_size=0.2,

        random_state=42

    )


# ==========================================
# Train Model
# ==========================================

def train_model(

        X_train,

        y_train

):

    model = LinearRegression()

    model.fit(

        X_train,

        y_train

    )

    return model


# ==========================================
# Evaluate Model
# ==========================================

def evaluate_model(

        model,

        X_test,

        y_test

):

    prediction = model.predict(

        X_test

    )

    mae = mean_absolute_error(

        y_test,

        prediction

    )

    rmse = mean_squared_error(

        y_test,

        prediction

    ) ** 0.5

    r2 = r2_score(

        y_test,

        prediction

    )

    return (

        prediction,

        mae,

        rmse,

        r2

    )


# ==========================================
# Save Model
# ==========================================

def save_model(model):

    joblib.dump(

        model,

        MODEL

    )


# ==========================================
# Save Report
# ==========================================

def save_report(

        df,

        mae,

        rmse,

        r2

):

    with open(

        REPORT,

        "w"

    ) as file:

        file.write(

            "GRADE PREDICTION MODEL REPORT\n"

        )

        file.write(

            "=============================\n\n"

        )

        file.write(

            f"Dataset Size : {len(df)}\n"

        )

        file.write(

            f"Number of Features : 4\n\n"

        )

        file.write(

            f"MAE : {mae:.3f}\n"

        )

        file.write(

            f"RMSE : {rmse:.3f}\n"

        )

        file.write(

            f"R2 Score : {r2:.3f}\n"

        )


# ==========================================
# Save Coefficients
# ==========================================

def save_coefficients(

        model,

        X

):

    coefficient = pd.DataFrame(

        {

            "Feature": X.columns,

            "Coefficient": model.coef_

        }

    )

    coefficient.to_csv(

        COEFFICIENT,

        index=False

    )


# ==========================================
# Display Result
# ==========================================

def print_result(

        df,

        mae,

        rmse,

        r2

):

    print()

    print("=" * 50)

    print("GRADE PREDICTION MODEL")

    print("=" * 50)

    print()

    print(

        "Dataset Size :", len(df)

    )

    print(

        "Training Finished Successfully"

    )

    print()

    print(

        f"MAE  : {mae:.3f}"

    )

    print(

        f"RMSE : {rmse:.3f}"

    )

    print(

        f"R2   : {r2:.3f}"

    )

    print()

    print(

        "Model Saved :", MODEL

    )

    print(

        "Report Saved :", REPORT

    )

    print(

        "Coefficient Saved :", COEFFICIENT

    )

    print()


# ==========================================
# Main
# ==========================================

def main():

    print()

    print("Loading Dataset...")

    df = load_dataset()

    if len(df) < 30:

        print()

        print(

            "Warning : Dataset is very small."

        )

        print(

            "Prediction accuracy may not be reliable."

        )

        print()

    X, y = prepare_data(df)

    X_train, X_test, y_train, y_test = split_dataset(

        X,

        y

    )

    print(

        "Training Model..."

    )

    model = train_model(

        X_train,

        y_train

    )

    print(

        "Evaluating Model..."

    )

    prediction, mae, rmse, r2 = evaluate_model(

        model,

        X_test,

        y_test

    )

    print(

        "Saving Model..."

    )

    save_model(model)

    save_report(

        df,

        mae,

        rmse,

        r2

    )

    save_coefficients(

        model,

        X

    )

    print_result(

        df,

        mae,

        rmse,

        r2

    )


if __name__ == "__main__":

    main()