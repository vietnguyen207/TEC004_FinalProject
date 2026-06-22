"""
SP2 - File I/O Module
University Course Performance Tracker & Grade Prediction System
TEC004/05

Features:
  - Import grades from CSV (midterm, final, assignments)
  - Export reports to JSON
  - Batch processing of multiple class files using multi-threading
"""

import csv
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────
# CSV Importer
# ─────────────────────────────────────────────

class CSVImporter:
    """
    Reads grade CSVs with the expected column layout:

    student_id, name, midterm, final, a1, a2, a3, ..., attendance
    """

    REQUIRED_COLS = {"student_id", "name", "midterm", "final", "attendance"}

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self._raw_rows: list[dict] = []
        self._errors: list[str] = []

    # ── Lambda helpers ─────────────────────────
    _to_float   = staticmethod(lambda v: float(v) if v.strip() else 0.0)
    _is_assign  = staticmethod(lambda col: col.startswith("a") and col[1:].isdigit())

    def load(self) -> list[dict]:
        """Parse CSV and return list of student grade dicts."""
        if not self.filepath.exists():
            raise FileNotFoundError(f"CSV not found: {self.filepath}")

        with open(self.filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = set(reader.fieldnames or [])

            missing = self.REQUIRED_COLS - headers
            if missing:
                raise ValueError(f"CSV missing required columns: {missing}")

            for i, row in enumerate(reader, start=2):   # row 1 = header
                try:
                    record = self._parse_row(row)
                    self._raw_rows.append(record)
                except Exception as e:
                    self._errors.append(f"Row {i}: {e}")

        if self._errors:
            print(f"[CSVImporter] {len(self._errors)} row error(s) in {self.filepath.name}:")
            for err in self._errors:
                print(f"  {err}")

        return self._raw_rows

    def _parse_row(self, row: dict) -> dict:
        assignments = list(map(
            self._to_float,
            [v for k, v in row.items() if self._is_assign(k)]
        ))
        return {
            "student_id":  row["student_id"].strip(),
            "name":        row["name"].strip(),
            "midterm":     self._to_float(row["midterm"]),
            "final":       self._to_float(row["final"]),
            "assignments": assignments,
            "attendance":  self._to_float(row["attendance"]),
        }

    @property
    def errors(self):
        return list(self._errors)


# ─────────────────────────────────────────────
# JSON Exporter
# ─────────────────────────────────────────────

class JSONExporter:
    """Serialises grade report data to a JSON file."""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(self, course_id: str, records: list[dict],
               stats: Optional[dict] = None) -> str:
        """
        Write a grade report.  Returns the path of the saved file.
        """
        payload = {
            "course_id":   course_id,
            "generated_at": datetime.now().isoformat(),
            "stats":        stats or {},
            "records":      records,
        }
        filename = self.output_dir / f"{course_id}_report_{datetime.now():%Y%m%d_%H%M%S}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        print(f"[JSONExporter] Report saved → {filename}")
        return str(filename)

    def export_bulk(self, reports: list[tuple[str, list[dict], dict]]) -> list[str]:
        """Export multiple course reports. Returns list of saved paths."""
        return [self.export(cid, recs, stats) for cid, recs, stats in reports]


# ─────────────────────────────────────────────
# Batch Processor (multi-threading)
# ─────────────────────────────────────────────

class BatchFileProcessor:
    """
    Processes a folder of CSV grade files concurrently using ThreadPoolExecutor.
    Each file is loaded, validated, and optionally exported as JSON.
    """

    def __init__(self, input_dir: str, output_dir: str = "reports",
                 max_workers: int = 4):
        self.input_dir  = Path(input_dir)
        self.output_dir = output_dir
        self.max_workers = max_workers
        self._lock = threading.Lock()
        self._results: list[dict] = []
        self._failed:  list[str]  = []

    def run(self, export_json: bool = True) -> list[dict]:
        """
        Discover all .csv files in input_dir and process them concurrently.
        Returns a list of per-file result dicts.
        """
        csv_files = sorted(self.input_dir.glob("*.csv"))
        if not csv_files:
            print(f"[BatchProcessor] No CSV files found in {self.input_dir}")
            return []

        print(f"[BatchProcessor] Found {len(csv_files)} file(s). "
              f"Starting with {self.max_workers} workers…")

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = {
                pool.submit(self._process_file, f, export_json): f
                for f in csv_files
            }
            for future in as_completed(futures):
                filepath = futures[future]
                try:
                    result = future.result()
                    with self._lock:
                        self._results.append(result)
                    print(f"  ✓ {filepath.name}  ({result['row_count']} rows)")
                except Exception as e:
                    with self._lock:
                        self._failed.append(filepath.name)
                    print(f"  ✗ {filepath.name}: {e}")

        print(f"[BatchProcessor] Done. "
              f"Success: {len(self._results)}, Failed: {len(self._failed)}")
        return self._results

    def _process_file(self, filepath: Path, export_json: bool) -> dict:
        """Worker: load one CSV and (optionally) export JSON."""
        importer = CSVImporter(str(filepath))
        records  = importer.load()

        # Derive course_id from filename (e.g. CS101_grades.csv → CS101)
        course_id = filepath.stem.split("_")[0].upper()

        # Simple stats using map/reduce (advanced functions)
        finals = list(map(lambda r: r["final"], records))
        avg_final = reduce(lambda a, b: a + b, finals) / len(finals) if finals else 0.0
        passed    = list(filter(lambda r: r["final"] >= 60, records))
        stats = {
            "row_count":  len(records),
            "avg_final":  round(avg_final, 2),
            "pass_count": len(passed),
            "fail_count": len(records) - len(passed),
        }

        out_path = None
        if export_json:
            exporter = JSONExporter(self.output_dir)
            out_path = exporter.export(course_id, records, stats)

        return {"course_id": course_id, "row_count": len(records),
                "stats": stats, "json_path": out_path,
                "errors": importer.errors}

    @property
    def failed_files(self):
        return list(self._failed)


# ─────────────────────────────────────────────
# Utility helpers
# ─────────────────────────────────────────────

def create_sample_csv(filepath: str, num_students: int = 5):
    """Generate a sample CSV for testing."""
    import random, string
    random.seed(42)

    headers = ["student_id", "name", "midterm", "final",
               "a1", "a2", "a3", "attendance"]
    rows = []
    for i in range(1, num_students + 1):
        sid  = f"S{i:03d}"
        name = f"Student_{i}"
        rows.append({
            "student_id": sid,
            "name":       name,
            "midterm":    round(random.uniform(50, 100), 1),
            "final":      round(random.uniform(50, 100), 1),
            "a1":         round(random.uniform(60, 100), 1),
            "a2":         round(random.uniform(60, 100), 1),
            "a3":         round(random.uniform(60, 100), 1),
            "attendance": round(random.uniform(70, 100), 1),
        })

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    print(f"[util] Sample CSV created → {filepath}")


# ─────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import tempfile, shutil

    # 1. Create temp directory with sample CSVs
    tmpdir = tempfile.mkdtemp()
    for course in ["CS101", "CS102", "MATH201"]:
        create_sample_csv(f"{tmpdir}/{course}_grades.csv", num_students=6)

    # 2. Batch-process all CSVs concurrently
    processor = BatchFileProcessor(input_dir=tmpdir,
                                   output_dir=f"{tmpdir}/reports",
                                   max_workers=3)
    results = processor.run(export_json=True)

    # 3. Show summary
    print("\n── Summary ──")
    for r in results:
        print(f"  {r['course_id']}: {r['row_count']} students | "
              f"avg final={r['stats']['avg_final']}")

    # Cleanup
    shutil.rmtree(tmpdir)
    print("\nTemp files cleaned up.")
