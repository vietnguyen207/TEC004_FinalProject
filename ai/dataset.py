import os
from config import DATASET_PATH
from feature_builder import (
    get_connection,
    build_all_features
)

OUTPUT_DIR = os.path.dirname(__file__)

OUTPUT_FILE = DATASET_PATH


def export_training_dataset():

    print("Loading Database...")

    conn = get_connection()

    dataset = build_all_features(conn)

    conn.close()

    dataset.to_csv(

        OUTPUT_FILE,

        index=False

    )

    print()

    print("Dataset Saved")

    print()

    print(dataset.head())

    print()

    print("Rows :", len(dataset))

    print("Columns :", len(dataset.columns))

    return dataset


if __name__ == "__main__":

    export_training_dataset()