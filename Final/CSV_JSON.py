import sqlite3
import csv
import json
import os
from concurrent.futures import ThreadPoolExecutor
from BaseClasses import WeightedGrading
DB_NAME = "database_fp.db"

def import_csv_to_db(csv_path):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    # Load all valid student IDs

    cursor.execute("""
        SELECT student_id
        FROM students
    """)

    student_ids = {
        row[0]
        for row in cursor.fetchall()
    }

    # Load all valid course IDs

    cursor.execute("""
        SELECT course_id
        FROM courses
    """)

    course_ids = {
        row[0]
        for row in cursor.fetchall()
    }

    imported = 0
    updated = 0
    skipped = 0

    errors = []

    with open(
        csv_path,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            student_id = row["student_id"].strip()
            course_id = row["course_id"].strip()

            # Validation

            if student_id not in student_ids:

                skipped += 1

                errors.append(
                    f"Student ID '{student_id}' not found"
                )

                continue

            if course_id not in course_ids:

                skipped += 1

                errors.append(
                    f"Course ID '{course_id}' not found"
                )

                continue

            assignment = float(
                row["assignment"]
            )

            midterm = float(
                row["midterm"]
            )

            final = float(
                row["final"]
            )
            grade = WeightedGrading(
                assignment,
                midterm,
                final
            )
            final_grade = grade.calculate_grade()

            # Check whether record exists

            cursor.execute(
                """
                SELECT grade_id

                FROM grades

                WHERE student_id = ?
                AND course_id = ?
                """,
                (
                    student_id,
                    course_id
                )
            )

            existing = cursor.fetchone()

            if existing:

                cursor.execute(
                    """
                    UPDATE grades

                    SET
                        assignment = ?,
                        midterm = ?,
                        final = ?,
                        final_grade = ?

                    WHERE
                        student_id = ?
                    AND
                        course_id = ?
                    """,
                    (
                        assignment,
                        midterm,
                        final,
                        final_grade,
                        student_id,
                        course_id
                    )
                )

                updated += 1

            else:

                cursor.execute(
                    """
                    INSERT INTO grades
                    (
                        student_id,
                        course_id,
                        assignment,
                        midterm,
                        final,
                        final_grade
                    )
                    VALUES
                    (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        student_id,
                        course_id,
                        assignment,
                        midterm,
                        final,
                        final_grade
                    )
                )

                imported += 1

    conn.commit()

    conn.close()

    return {
        "imported": imported,
        "updated": updated,
        "skipped": skipped,
        "errors": errors
    }

def import_multiple_csv(file_paths):

    total_imported = 0
    total_updated = 0
    total_skipped = 0

    all_errors = []

    with ThreadPoolExecutor(
        max_workers=5
    ) as executor:

        futures = []

        for path in file_paths:

            futures.append(
                executor.submit(
                    import_csv_to_db,
                    path
                )
            )

        for future in futures:

            result = future.result()

            total_imported += result["imported"]

            total_updated += result["updated"]

            total_skipped += result["skipped"]

            all_errors.extend(
                result["errors"]
            )

    return {
        "imported": total_imported,
        "updated": total_updated,
        "skipped": total_skipped,
        "errors": all_errors
    }



def export_report_json():

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            g.grade_id,

            s.student_id,
            s.name AS student_name,

            c.course_id,
            c.course_name,

            g.assignment,
            g.midterm,
            g.final,

            g.final_grade

        FROM grades g

        INNER JOIN students s
            ON g.student_id = s.student_id

        INNER JOIN courses c
            ON g.course_id = c.course_id

        ORDER BY
            s.student_id,
            c.course_id
    """)

    rows = cursor.fetchall()

    report = []

    for row in rows:

        report.append({
            "grade_id": row["grade_id"],
            "student_id": row["student_id"],
            "student_name": row["student_name"],
            "course_id": row["course_id"],
            "course_name": row["course_name"],
            "assignment": row["assignment"],
            "midterm": row["midterm"],
            "final": row["final"],
            "final_grade": row["final_grade"]
        })

    conn.close()

    filename = os.path.abspath("grade_report.json")

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )

    return filename