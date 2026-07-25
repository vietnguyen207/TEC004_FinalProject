from functools import wraps

from flask import session
from flask import redirect
from flask import url_for

def login_required(f):

    @wraps(f)

    def wrapper(*args,**kwargs):

        if "username" not in session:

            return redirect(
                url_for("auth.login")
            )

        return f(*args,**kwargs)

    return wrapper

def admin_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):


        if session.get("role") != "admin":
            
            return redirect(url_for("auth.login"))

        

        return f(*args, **kwargs)

    return wrapper

def instructor_required(f):

    @wraps(f)

    def wrapper(*args,**kwargs):

        if session.get("role")!="instructor":

            return redirect(
                url_for("auth.login")
            )

        return f(*args,**kwargs)

    return wrapper

def student_required(f):

    @wraps(f)

    def wrapper(*args,**kwargs):

        if session.get("role")!="student":

            return redirect(
                url_for("auth.login")
            )

        return f(*args,**kwargs)

    return wrapper