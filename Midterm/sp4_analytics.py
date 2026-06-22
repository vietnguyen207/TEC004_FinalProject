"""
SP4 - Analytics Engine
University Course Performance Tracker & Grade Prediction System
TEC004/05

Pandas-based analysis including:
  - Grade distributions
  - Pass/fail rates
  - Correlation between attendance and grades
  - Midterm vs final performance
  - Semester-over-semester trends
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────
# GradeAnalytics
# ─────────────────────────────────────────────

class GradeAnalytics:
    """
    Accepts a DataFrame with the columns:
      student_id, name, course_id, semester,
      midterm, final, attendance, assignments_avg, final_grade, credits
    """

    REQUIRED = {"student_id", "course_id", "semester",
                "midterm", "final", "attendance", "final_grade"}

    def __init__(self, df: pd.DataFrame):
        missing = self.REQUIRED - set(df.columns)
        if missing:
            raise ValueError(f"DataFrame missing columns: {missing}")
        self.df = df.copy()
        self._add_derived_columns()

    # ── Preparation ────────────────────────────

    def _add_derived_columns(self):
        self.df["letter"] = self.df["final_grade"].apply(self._to_letter)
        self.df["passed"] = self.df["final_grade"] >= 60

    @staticmethod
    def _to_letter(score: float) -> str:
        if score >= 90: return "A"
        if score >= 80: return "B"
        if score >= 70: return "C"
        if score >= 60: return "D"
        return "F"

    # ─────────────────────────────────────────
    # 1. Grade Distribution
    # ─────────────────────────────────────────

    def grade_distribution(self, course_id: Optional[str] = None) -> pd.DataFrame:
        """
        Count of each letter grade across all courses (or one course).
        Returns a DataFrame with columns: letter, count, pct
        """
        data = self.df[self.df.course_id == course_id] if course_id else self.df
        dist = (data["letter"]
                .value_counts()
                .reindex(["A", "B", "C", "D", "F"], fill_value=0)
                .reset_index())
        dist.columns = ["letter", "count"]
        dist["pct"] = (dist["count"] / dist["count"].sum() * 100).round(1)
        return dist

    def score_histogram_bins(self, course_id: Optional[str] = None,
                             bins: int = 10) -> pd.DataFrame:
        """Bin final_grade into histogram buckets."""
        data = self.df[self.df.course_id == course_id] if course_id else self.df
        counts, edges = np.histogram(data["final_grade"].dropna(),
                                     bins=bins, range=(0, 100))
        labels = [f"{int(edges[i])}–{int(edges[i+1])}" for i in range(len(counts))]
        return pd.DataFrame({"range": labels, "count": counts})

    # ─────────────────────────────────────────
    # 2. Pass/Fail Rates
    # ─────────────────────────────────────────

    def pass_fail_by_course(self) -> pd.DataFrame:
        """Pass and fail counts + pass-rate per course."""
        grp = (self.df.groupby("course_id")["passed"]
               .agg(total="count",
                    passed=lambda x: x.sum(),
                    failed=lambda x: (~x).sum()))
        grp["pass_rate_pct"] = (grp["passed"] / grp["total"] * 100).round(1)
        return grp.reset_index().sort_values("pass_rate_pct")

    def pass_fail_overall(self) -> dict:
        n = len(self.df)
        p = self.df["passed"].sum()
        return {"total": n, "passed": int(p), "failed": int(n - p),
                "pass_rate_pct": round(p / n * 100, 1) if n else 0.0}

    # ─────────────────────────────────────────
    # 3. Correlation Analysis
    # ─────────────────────────────────────────

    def attendance_grade_correlation(self) -> dict:
        """
        Pearson correlation between attendance and final_grade.
        Includes a simple interpretation.
        """
        r = self.df[["attendance", "final_grade"]].dropna().corr().iloc[0, 1]
        r = round(r, 4)
        if abs(r) >= 0.7:   strength = "strong"
        elif abs(r) >= 0.4: strength = "moderate"
        else:               strength = "weak"
        direction = "positive" if r > 0 else "negative"
        return {
            "pearson_r": r,
            "interpretation": f"{strength} {direction} correlation",
        }

    def midterm_final_correlation(self) -> dict:
        """Correlation between midterm and final scores."""
        r = self.df[["midterm", "final"]].dropna().corr().iloc[0, 1]
        r = round(r, 4)
        if abs(r) >= 0.7:   strength = "strong"
        elif abs(r) >= 0.4: strength = "moderate"
        else:               strength = "weak"
        direction = "positive" if r > 0 else "negative"
        return {
            "pearson_r": r,
            "interpretation": f"{strength} {direction} correlation",
        }

    def correlation_matrix(self) -> pd.DataFrame:
        """Full correlation matrix for numeric columns."""
        cols = ["midterm", "final", "attendance", "final_grade"]
        available = [c for c in cols if c in self.df.columns]
        return self.df[available].corr().round(3)

    # ─────────────────────────────────────────
    # 4. Semester-over-Semester Trends
    # ─────────────────────────────────────────

    def semester_trend(self) -> pd.DataFrame:
        """
        Average final_grade, pass rate, and student count per semester.
        Sorted chronologically.
        """
        grp = self.df.groupby("semester").agg(
            avg_grade   = ("final_grade", "mean"),
            pass_rate   = ("passed",      lambda x: x.mean() * 100),
            avg_midterm = ("midterm",     "mean"),
            avg_final   = ("final",       "mean"),
            student_cnt = ("student_id",  "nunique"),
        ).round(2)
        return grp.reset_index().sort_values("semester")

    def course_difficulty_comparison(self) -> pd.DataFrame:
        """
        Compare courses by average grade (proxy for difficulty).
        Lower average → harder course.
        """
        grp = self.df.groupby("course_id").agg(
            avg_grade     = ("final_grade", "mean"),
            std_grade     = ("final_grade", "std"),
            pass_rate_pct = ("passed",      lambda x: x.mean() * 100),
            enrolled      = ("student_id",  "count"),
        ).round(2).reset_index()
        grp["difficulty_rank"] = grp["avg_grade"].rank(ascending=True).astype(int)
        return grp.sort_values("difficulty_rank")

    # ─────────────────────────────────────────
    # 5. Student-level Summary
    # ─────────────────────────────────────────

    def student_summary(self, student_id: str) -> dict:
        sub = self.df[self.df.student_id == student_id]
        if sub.empty:
            return {}
        return {
            "student_id":   student_id,
            "courses_taken": len(sub),
            "avg_grade":    round(sub["final_grade"].mean(), 2),
            "avg_midterm":  round(sub["midterm"].mean(), 2),
            "avg_final":    round(sub["final"].mean(), 2),
            "avg_attendance": round(sub["attendance"].mean(), 2),
            "pass_rate":    round(sub["passed"].mean() * 100, 1),
        }

    def at_risk_report(self,
                       grade_thresh: float = 60.0,
                       attend_thresh: float = 75.0) -> pd.DataFrame:
        """Students below grade or attendance thresholds."""
        mask = (self.df["final_grade"] < grade_thresh) | \
               (self.df["attendance"]  < attend_thresh)
        cols = ["student_id", "name", "course_id", "semester",
                "final_grade", "attendance", "letter"]
        available = [c for c in cols if c in self.df.columns]
        return (self.df[mask][available]
                .sort_values("final_grade")
                .reset_index(drop=True))

    # ─────────────────────────────────────────
    # 6. Printable report
    # ─────────────────────────────────────────

    def print_full_report(self):
        print("\n" + "="*60)
        print("  GRADE ANALYTICS REPORT")
        print("="*60)

        print("\n── Overall Pass/Fail ──")
        print(" ", self.pass_fail_overall())

        print("\n── Pass Rate by Course ──")
        print(self.pass_fail_by_course().to_string(index=False))

        print("\n── Grade Distribution (all courses) ──")
        print(self.grade_distribution().to_string(index=False))

        print("\n── Attendance ↔ Final Grade Correlation ──")
        print(" ", self.attendance_grade_correlation())

        print("\n── Midterm ↔ Final Correlation ──")
        print(" ", self.midterm_final_correlation())

        print("\n── Semester Trend ──")
        print(self.semester_trend().to_string(index=False))

        print("\n── Course Difficulty Comparison ──")
        print(self.course_difficulty_comparison().to_string(index=False))

        at_risk = self.at_risk_report()
        print(f"\n── At-Risk Students ({len(at_risk)}) ──")
        if not at_risk.empty:
            print(at_risk.to_string(index=False))
        else:
            print("  None found.")

        print("\n" + "="*60 + "\n")


# ─────────────────────────────────────────────
# Sample data factory
# ─────────────────────────────────────────────

def make_sample_dataframe(n: int = 40, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic grade data for testing."""
    rng = np.random.default_rng(seed)
    courses   = ["CS101", "CS102", "MATH201", "ENG101"]
    semesters = ["2023-S1", "2023-S2", "2024-S1"]

    rows = []
    for i in range(n):
        sid      = f"S{i+1:03d}"
        course   = rng.choice(courses)
        sem      = rng.choice(semesters)
        attend   = float(rng.uniform(60, 100))
        midterm  = float(rng.uniform(45, 100))
        # final correlated with midterm + attendance
        final    = float(np.clip(midterm * 0.6 + attend * 0.2 + rng.normal(0, 5), 0, 100))
        asgn_avg = float(rng.uniform(55, 100))
        fg       = round(midterm * 0.30 + final * 0.40 + asgn_avg * 0.20 + attend * 0.10, 2)
        rows.append({
            "student_id":     sid,
            "name":           f"Student_{i+1}",
            "course_id":      course,
            "semester":       sem,
            "midterm":        round(midterm, 1),
            "final":          round(final, 1),
            "attendance":     round(attend, 1),
            "assignments_avg": round(asgn_avg, 1),
            "final_grade":    round(fg, 2),
            "credits":        3,
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────

if __name__ == "__main__":
    df      = make_sample_dataframe(n=60)
    engine  = GradeAnalytics(df)
    engine.print_full_report()

    # Per-student example
    print("── Student S001 Summary ──")
    print(" ", engine.student_summary("S001"))

    # Histogram bins for CS101
    print("\n── CS101 Score Histogram ──")
    print(engine.score_histogram_bins("CS101").to_string(index=False))
