from flask import Flask, redirect, url_for, request
from backend.login import login_bp
from backend.admin import admin_bp
from backend.quiz import quiz_bp
from backend.profile import profile_bp
from backend.student import student_bp

import time
app = Flask(__name__)
app.secret_key = '1234'


app.register_blueprint(login_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(student_bp)

if __name__ == '__main__':
    app.run(debug=True)
