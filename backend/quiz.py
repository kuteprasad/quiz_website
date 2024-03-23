from flask import Blueprint, jsonify, render_template, session, request
from backend.database import get_test_data, show_users_data

quiz_bp = Blueprint('quiz', __name__)

test_id = 0

@quiz_bp.route('/home/<username>')
def index(username):
    # Check if user is logged in
    if 'username' in session:
        # Pass the 'username' variable to the template
        username = session['username']
        return render_template('test_section/home.html', username=username)
    else:
        return redirect(url_for('login.index'))

@quiz_bp.route('/start-quiz', methods=['POST'])
def start_quiz():
    # global current_data  # Access the global current_data variable
    global test_id

    username = request.form['username']
    test_id = int(request.form['test'])

    current_data = get_test_data(test_id)
    # print(current_data)
    index = 0
    timer_value = 30
    return render_template('test_section/quiz.html', row_data=current_data, index=index, timer_value=timer_value, username = username)

@quiz_bp.route('/submit/<int:index>', methods=['POST'])
def submit(index):
    
    global test_id
    username = request.form['username']
    print(username)
    total_correct = int(request.form['total_score'])

    # print("user :" + username )
    print(total_correct)

    data = show_users_data('student', username, test_id)
    # print(data)
    return render_template('test_section/result.html', row_data = data, total_correct = total_correct, username = username) 