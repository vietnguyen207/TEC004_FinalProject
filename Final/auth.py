from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from flask import url_for

import sqlite3

DATABASE="database_fp.db"

auth_bp=Blueprint(
    "auth",
    __name__
)

@auth_bp.route("/",methods=["GET","POST"])
def login():

    if request.method=="POST":
        role=request.form["role"]

        username=request.form["username"]

        password=request.form["password"]

        conn=sqlite3.connect(DATABASE)

        conn.row_factory=sqlite3.Row

        cursor=conn.cursor()

        cursor.execute("""

            SELECT *

            FROM users

            WHERE username=?

            AND password=?

            AND role=?

        """,(username, password, role))

        user=cursor.fetchone()

        conn.close()

        if user:

            session["username"]=user["username"]

            session["role"]=user["role"]

            session["user_id"]=user["user_id"]

            if user["role"]=="admin":

                return redirect(url_for("admin.dashboard"))

            elif user["role"]=="instructor":

                return redirect(url_for("instructor.dashboard"))

            else:

                return redirect(url_for("student.dashboard"))

        return render_template(
            "login.html",
            error="Wrong username or password"
        )

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("auth.login"))