from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2, time

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

def return_table_name(user):
    if user == 'admin':
        table_name = "accounts_admin"
    else:
        table_name = "accounts"
    return table_name

# Function to check if username and password are correct
def authenticate_user(user, username, password):

    table_name = return_table_name(user)
    # print(table_name)
    conn = connect_to_db()
    cursor = conn.cursor()
    query = f"SELECT password FROM {table_name} WHERE username = %s"
    cursor.execute(query, (username,))
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

def getTestData(test_number):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM test_data WHERE test_id = %s", (test_number,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# --------------------- # --------------- Login Section --------------- # ----------------------- #
@app.route('/')
def index():
    return render_template('start_here.html')

@app.route('/login', methods=['GET'])
def login_get():
    user = request.args.get('user')
    # print(user)
    if(user == 'student' or user == 'admin' ):
        return render_template('login.html', user = user)
    else:
        return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    # Get form data
    user = request.form['user']
    username = request.form['username']
    password = request.form['password']

    # print(user)
    # Check if username and password exist in the database
    auth_result = authenticate_user(user, username, password)
    if auth_result is True:
        # If username and password are correct, set session variable and redirect to quiz page or admin page
        session['username'] = username

        if(user == 'admin'):
            return redirect(url_for('admin', username = username))
        else:
            return redirect(url_for('home' , username = username))

    elif auth_result is False:
        # If username is found but password is incorrect, show error message
        return "Password incorrect. Please try again."
    else:
        # If username is not found, show error message
        return "User not found. Please register first."
    
@app.route('/signup', methods=['GET'])
def signup():
    user = request.args.get('user')
    # print(user)
    return render_template('signup.html', user = user)

@app.route('/signup_submit', methods=['POST'])
def signup_submit():
    # Get form data
    user = request.form['user']
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    table_name = return_table_name(user)

    try:
        # Establish a connection to the database
        conn = connect_to_db()
        cursor = conn.cursor()

        # Execute SQL INSERT query to insert user data into the database
        query = f"INSERT INTO {table_name} (username, email, password) VALUES (%s, %s, %s);"
        cursor.execute(query, ( username, email, password))
        
        # Commit the transaction
        conn.commit()
        
        # Close the cursor and database connection
        cursor.close()
        conn.close()
        
        # Redirect to login page
        return render_template('login.html', user = user)

    except psycopg2.Error as e:
        # Check if the error is due to a duplicate key violation
        if e.pgcode == '23505':
            # If username already exists, return "User already exists"
            return "User already exists. Please choose a different username."
        else:
            # If the error is not a duplicate key violation, print the error
            print("Error occurred:", e)
            return "An error occurred. Please try again later."

@app.route('/home/<username>')
def home(username):
    # Check if user is logged in
    if 'username' in session:
        # Pass the 'username' variable to the template
        username = session['username']
        return render_template('home.html', username=username)
    else:
        return redirect(url_for('index'))

# --------------------- # --------------- Login Section Ends --------------- # ----------------------- #

# --------------------- # --------------- Admin Section --------------- # ----------------------- #
@app.route('/admin/<username>')
def admin(username):
    return "welcome to admin portal " + username.capitalize() + " !"
# --------------------- # --------------- Admin Section Ends --------------- # ----------------------- #

# --------------------- # --------------- Quiz Section --------------- # ----------------------- #
current_data = []
total_correct_answers = {}

# Quiz logic
@app.route('/start-quiz', methods=['POST'])
def start_quiz():
    global current_data  # Access the global current_data variable
    # Get form data: test name
    test_number = int(request.form['test'])

    current_data = getTestData(test_number)

    index = 0
    timer_value = 600
    # return "success"
    return render_template('quiz.html', row_data=current_data, index=index, timer_value = timer_value)

@app.route('/submit/<int:index>', methods=['POST'])
def submit(index):
    global total_correct_answers
    global current_data  # Access the global current_data variable

    # question_number = index + 1
    correct_answer = request.form.get('correct_answer')
    user_chosen_answer = request.form.get('answer')
    current_countdown_seconds = int(request.form.get('timer_value_updated'))

    total_correct_answers[index] = (user_chosen_answer, correct_answer)


    if request.method == 'POST':
        if 'next' in request.form:
            # Next button was clicked
            # Perform the desired action
            index += 1

            # Render the quiz.html template with the next question and options
            # return render_template('quiz.html', row_data = current_data, index=index)
            # return "next is clicked"
        elif 'prev' in request.form:
            # Previous button was clicked
            # Perform the desired action
            index -= 1

            # Render the quiz.html template with the previous question and options
            # return render_template('quiz.html', row_data = current_data, index=index)
            # return "prev is clicked"
        elif 'submit' in request.form:
            # Submit button was clicked
            # Perform the desired action
            total_correct = 0
            for answer, correct in total_correct_answers.values():
                if answer == correct:
                    total_correct += 4
                else:
                    total_correct -= 1

            return render_template('result.html', total_correct = total_correct)
        else:
            # Handle other cases if needed
            return "Some error occured"
    return render_template('quiz.html', row_data = current_data, index=index, timer_value = current_countdown_seconds)
    # Logic to handle submission of answers and calculate total correct answers
    # return "the mcq's are submitted"
# --------------------- # --------------- Quiz Section Ends --------------- # ----------------------- #

# Route to print all users in the console
@app.route('/print_users')
def print_users():
    users = fetch_all_users()
    for user in users:
        print(user)
    return "Check console for all users"

if __name__ == '__main__':
    app.run( debug=True)
    # app.run(host='0.0.0.0', port=3000, debug=True)
