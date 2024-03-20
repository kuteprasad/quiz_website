from flask import Blueprint, jsonify, render_template, session, request
from backend.database import getTestData, show_users_data

quiz_bp = Blueprint('quiz', __name__)

# total_correct_answers = {}
# current_data = []
# username = ''
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

    current_data = getTestData(test_id)
    # print(current_data)
    index = 0
    timer_value = 20
    return render_template('test_section/quiz.html', row_data=current_data, index=index, timer_value=timer_value, username = username)

@quiz_bp.route('/submit/<int:index>', methods=['POST'])
def submit(index):
    # global total_correct_answers
    # global current_data  # Access the global current_data variable
    global test_id
    username = request.form['username']
    print(username)
    total_correct = int(request.form['total_score'])

    # print("user :" + username )
    print(total_correct)
    # question_number = index + 1
    # correct_answer = request.form.get('correct_answer')
    # user_chosen_answer = request.form.get('answer')
    # current_countdown_seconds = int(request.form.get('timer_value_updated'))

    # total_correct_answers[index] = (user_chosen_answer, correct_answer)
    


    # if request.method == 'POST':
        # if 'next' in request.form:
            # Next button was clicked
            # Perform the desired action
            # index += 1

            # Render the quiz.html template with the next question and options
            # return render_template('quiz.html', row_data = current_data, index=index)
            # return "next is clicked"
        # elif 'prev' in request.form:
            # Previous button was clicked
            # Perform the desired action
            # index -= 1

            # Render the quiz.html template with the previous question and options
            # return render_template('quiz.html', row_data = current_data, index=index)
            # return "prev is clicked"
        # elif 'submit' in request.form:
            # Submit button was clicked˝
            # Perform the desired action
    # total_correct = 0
    # for answer, correct in total_correct_answers.values():
    #     if answer == correct:
    #         total_correct += 4
    #     else:
    #         total_correct -= 1

    data = show_users_data('student', username, test_id)
    # print(data)
    return render_template('test_section/result.html', row_data = data, total_correct = total_correct, username = username)
        # else:
            # Handle other cases if needed
            # return "Some error occured"
    # return render_template('test_section/quiz.html', row_data = current_data, index=index, timer_value = current_countdown_seconds , username = username)
    # Logic to handle submission of answers and calculate total correct answers
    # return "the mcq's are submitted"
