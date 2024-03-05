from flask import Blueprint, render_template, session, request
from backend.database import show_users_data

student_bp = Blueprint('student', __name__)

@student_bp.route('/student/<username>')
def index(username):
    return render_template('student_side_pages/student_main.html', username = username)

@student_bp.route('/go_to_test_section')
def go_to_test_section():
    username = request.args.get('username')
    return render_template('test_section/home.html', username = username)

@student_bp.route('/view_previous_tests')
def view_previous_tests():
    username = request.args.get('username')
    # print(username)
    data = show_users_data('student', username)
    # print(data)
    return render_template('student_side_pages/view_data_student.html', row_data = data, username = username)
