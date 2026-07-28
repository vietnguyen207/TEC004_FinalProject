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
import math
from config import (

    FEATURE_COLUMNS,

    TARGET_COLUMN,

    TEST_SIZE,

    RANDOM_STATE,

    DATASET_PATH,

    MODEL_PATH

)
BASE_DIR = os.path.dirname(__file__)

CSV_FILE = DATASET_PATH


MODEL_FILE = MODEL_PATH




TARGET = TARGET_COLUMN


def load_dataset():

    return pd.read_csv(CSV_FILE)


def split_dataset(dataset):

    X = dataset[FEATURE_COLUMNS]

    y = dataset[TARGET]

    return train_test_split(

        X,

        y,

        test_size=TEST_SIZE,

        random_state=RANDOM_STATE

    )


def train_model(X_train, y_train):

    model = LinearRegression()

    model.fit(

        X_train,

        y_train

    )

    return model


def evaluate(model, X_test, y_test):

    prediction = model.predict(X_test)

    print()

    print("MAE :", mean_absolute_error(y_test, prediction))

    mse = mean_squared_error(
    y_test,
    prediction
    )

    rmse = math.sqrt(mse)

    print("RMSE :", rmse)

    print("R² :", r2_score(

        y_test,

        prediction

    ))

    print()


def save_model(model):

    joblib.dump(

        model,

        MODEL_FILE

    )

    print("Model Saved")


def main():

    dataset = load_dataset()

    X_train, X_test, y_train, y_test = split_dataset(dataset)

    model = train_model(

        X_train,

        y_train

    )

    evaluate(

        model,

        X_test,

        y_test

    )

    save_model(model)


if __name__ == "__main__":

    main()