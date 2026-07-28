from flask import Flask

from create_table import create_database
from auth import auth_bp
from admin import admin_bp
from instructor import instructor_bp
from student import student_bp
app = Flask(__name__)
create_database()
app.secret_key = "final_project_secret_key"

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(instructor_bp)
app.register_blueprint(student_bp)
if __name__ == "__main__":
    app.run(debug=True)
