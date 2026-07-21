from flask import session
from flask import request
from flask import Blueprint
import sqlite3
from flask import render_template, redirect


from flask import Blueprint
DATABASE = "database_fp.db"
login_bp = Blueprint("login", __name__)
@login_bp.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        role = request.form["role"]
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("""

        SELECT
            role,
            reference_id

        FROM users

        WHERE username=?
        AND password=?
        AND role=?

        """,

        (username,password,role))

        user = cursor.fetchone()

        conn.close()

        if user is None:

            return render_template(
                "login.html",
                error="Wrong username or password"
            )

        session["role"] = user[0]
        session["id"] = user[1]

        if role == "admin":

            return redirect("/admin")

        elif role == "instructor":

            return redirect("/instructor")

        elif role == "student":

            return redirect("/student")

    return render_template("login.html")