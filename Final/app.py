from flask import Flask

from create_table import create_database
from login import login_bp
from admin import admin_bp

app = Flask(__name__)
create_database() 
app.secret_key = "student"

app.register_blueprint(login_bp)
app.register_blueprint(admin_bp)
if __name__ == "__main__":
    app.run(debug=True)


    