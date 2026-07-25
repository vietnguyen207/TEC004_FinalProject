import sqlite3
from flask import Blueprint, render_template, request, redirect

student_bp = Blueprint("student", __name__)

@student_bp.route("/students")
def home():
    return render_template("student.html")
