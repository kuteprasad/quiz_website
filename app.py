from flask import Flask, redirect, url_for, request
from backend.login import login_bp
from backend.admin import admin_bp
from backend.quiz import quiz_bp
from backend.profile import profile_bp
from backend.student import student_bp

import time
app = Flask(__name__)

# Set a secret key for the Flask application
app.secret_key = 'this_is_truely_secret'  # Replace 'your_secret_key_here' with your actual secret key

app.register_blueprint(login_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(student_bp)

if __name__ == '__main__':
    app.run(debug=True)
