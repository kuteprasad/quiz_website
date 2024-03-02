from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2

app = Flask(__name__)
app.secret_key = '1234'

# PostgreSQL connection details
DB_NAME = 'quiz'
DB_USER = 'postgres'
DB_PASSWORD = 'india@11'
DB_HOST = 'localhost'

# Function to establish database connection
def connect_to_db():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
    )
    return conn

# Function to fetch all rows from the users table
def fetch_all_users():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Function to check if username and password are correct
def authenticate_user(username, password):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM accounts WHERE username = %s", (username,))
    row = cursor.fetchone()
    conn.close()

    if row:
        stored_password = row[0]
        if stored_password == password:
            return True  # Passwords match
        else:
            return False  # Incorrect password
    else:
        return None  # User not found

#functions of quiz
def get_question(question_number):
    # Sample questions with options and correct answers
    questions = [
        {
            "question": "What is the capital of France?",
            "options": ["London", "Paris", "Berlin", "Rome"],
            "correct_answer": "Paris"
        },
        {
            "question": "Which planet is known as the Red Planet?",
            "options": ["Mars", "Jupiter", "Saturn", "Venus"],
            "correct_answer": "Mars"
        },
        {
            "question": "Who wrote 'Romeo and Juliet'?",
            "options": ["William Shakespeare", "Charles Dickens", "Jane Austen", "Leo Tolstoy"],
            "correct_answer": "William Shakespeare"
        },
        {
            "question": "Which is the largest ocean on Earth?",
            "options": ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Pacific Ocean"],
            "correct_answer": "Pacific Ocean"
        },
        {
            "question": "What is the chemical symbol for water?",
            "options": ["H2O", "CO2", "O2", "H2SO4"],
            "correct_answer": "H2O"
        },
        {
            "question": "Who painted the Mona Lisa?",
            "options": ["Pablo Picasso", "Leonardo da Vinci", "Vincent van Gogh", "Michelangelo"],
            "correct_answer": "Leonardo da Vinci"
        },
        {
            "question": "What is the largest mammal in the world?",
            "options": ["Elephant", "Whale", "Giraffe", "Hippopotamus"],
            "correct_answer": "Whale"
        },
        {
            "question": "Which gas do plants use to photosynthesize?",
            "options": ["Oxygen", "Carbon dioxide", "Nitrogen", "Hydrogen"],
            "correct_answer": "Carbon dioxide"
        },
        {
            "question": "Who discovered penicillin?",
            "options": ["Isaac Newton", "Alexander Fleming", "Marie Curie", "Louis Pasteur"],
            "correct_answer": "Alexander Fleming"
        },
        {
            "question": "Which country is known as the Land of the Rising Sun?",
            "options": ["China", "India", "Japan", "South Korea"],
            "correct_answer": "Japan"
        }
    ]
    return questions[question_number - 1]  # Adjust index to match question number

def check_answer(question_number, answer):
    # Placeholder function to check user's answer
    # You need to implement your logic to validate the user's answer here
    return True  # Return True for now as a placeholder
# Routes
@app.route('/')
def index():
    return render_template('login.html')

#quiz logic
@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    # Logic to start the quiz
    return redirect(url_for('question', question_number=1))

@app.route('/question/<int:question_number>', methods=['GET', 'POST'])
def answer_question(question_number):
    if request.method == 'GET':
        # Logic to retrieve and display question
        question = get_question(question_number)
        return render_template('question.html', question=question)
    elif request.method == 'POST':
        # Logic to check answer and redirect to next question
        answer = request.form['answer']
        if check_answer(question_number, answer):
            # Increment correct answer count
            session['correct_answers'] += 1
        if question_number == 10:
            return redirect(url_for('result'))
        else:
            return redirect(url_for('question', question_number=question_number + 1))

@app.route('/result')
def result():
    correct_answers = session.get('correct_answers', 0)
    total_questions = 10
    return render_template('result.html', correct_answers=correct_answers, total_questions=total_questions)


@app.route('/login', methods=['GET'])
def login_get():
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    # Get form data
    username = request.form['username']
    password = request.form['password']

    # Check if username and password exist in the database
    auth_result = authenticate_user(username, password)
    if auth_result is True:
        # If username and password are correct, set session variable and redirect to quiz page
        session['username'] = username
        return redirect(url_for('quiz'))
    elif auth_result is False:
        # If username is found but password is incorrect, show error message
        return "Password incorrect. Please try again."
    else:
        # If username is not found, show error message
        return "User not found. Please register first."

@app.route('/quiz')
def quiz():
    # Check if user is logged in
    if 'username' in session:
        # Pass the 'username' variable to the template
        username = session['username']
        return render_template('quiz.html', username=username)
    else:
        return redirect(url_for('index'))
    
@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup_submit', methods=['POST'])
def signup_submit():
    # Get form data
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    try:
        # Establish a connection to the database
        conn = connect_to_db()
        cursor = conn.cursor()

        # Execute SQL INSERT query to insert user data into the database
        cursor.execute("INSERT INTO accounts (username, email, password) VALUES (%s, %s, %s);", (username, email, password))
        
        # Commit the transaction
        conn.commit()
        
        # Close the cursor and database connection
        cursor.close()
        conn.close()
        
        # Redirect to login page
        return redirect(url_for('index'))

    except psycopg2.Error as e:
        # Check if the error is due to a duplicate key violation
        if e.pgcode == '23505':
            # If username already exists, return "User already exists"
            return "User already exists. Please choose a different username."
        else:
            # If the error is not a duplicate key violation, print the error
            print("Error occurred:", e)
            return "An error occurred. Please try again later."

# Route to print all users in the console
@app.route('/print_users')
def print_users():
    users = fetch_all_users()
    for user in users:
        print(user)
    return "Check console for all users"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
