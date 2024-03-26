from flask import Blueprint, render_template, session, request, redirect, url_for
from backend.database import show_users_data, get_test_details

student_bp = Blueprint('student', __name__)

@student_bp.route('/student')
def index():
    return render_template('student_side_pages/student_main.html', username = session['username'])

@student_bp.route('/go_to_test_section')
def go_to_test_section():
    return redirect(url_for('quiz.index'))
    
@student_bp.route('/view_previous_tests')
def view_previous_tests():
   
    data = show_users_data(session['user'], session['username'])
    # print(data)
    # return "success"
    return render_template('student_side_pages/view_data_student.html', row_data = data, username = session['username'])
