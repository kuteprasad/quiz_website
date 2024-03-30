from flask import Blueprint, jsonify, render_template, session, request
from backend.database import get_test_data, show_users_data, get_test_details, add_users_data

quiz_bp = Blueprint('quiz', __name__)

# test_id = 0

@quiz_bp.route('/home')
def index():
    # Check if user is logged in
    if 'username' in session:
        data = get_test_details()
        # print(data)
        return render_template('test_section/home.html', data = data, username = session['username'])
    else:
        return redirect(url_for('login.index'))

@quiz_bp.route('/start-quiz', methods=['GET'])
def start_quiz_get():
    data = request.args
    return render_template('test_section/instructions.html', data = data)

@quiz_bp.route('/start-quiz', methods=['POST'])
def start_quiz():
    # global current_data  # Access the global current_data variable
    # global test_id
    print("requset. form of start-quiz post :: ")
    print(request.form)

    # username = request.form['username']
    test_id = int(request.form['test_id'])
    timer_value = int(request.form['test_duration'])

    data = get_test_data(test_id)
    # print(data)
    
    return render_template('test_section/quiz.html', row_data=data, index=0, timer_value=timer_value, username = session['username'])

@quiz_bp.route('/submit', methods=['POST'])
def submit():
    # global test_id
    username = session['username']
    test_id = int(request.form['test_id'])
    
    total_correct = int(request.form['total_score'])

    add_users_data(username, request.form)

    data = show_users_data('student', username, test_id)
    # print(data)
    return render_template('test_section/result.html', row_data = data, total_correct = total_correct, username = username) 

