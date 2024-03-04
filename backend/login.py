from flask import Blueprint, render_template, request, redirect, url_for, session
from backend.database import authenticate_user, return_table_name

login_bp = Blueprint('login', __name__)

@login_bp.route('/')
def index():
    # return "success"
    return render_template('start_here.html')

@login_bp.route('/login', methods=['GET'])
def login_get():
    user = request.args.get('user')
    if user in ['student', 'admin']:
        return render_template('login.html', user=user)
    else:
        return redirect(url_for('login.index'))

@login_bp.route('/login', methods=['POST'])
def login_post():
    user = request.form['user']
    username = request.form['username']
    password = request.form['password']

    auth_result = authenticate_user(user, username, password)
    if auth_result is True:
        session['username'] = username
        if user == 'admin':
            return redirect(url_for('admin.index', username=username))
        else:
            return redirect(url_for('quiz.index', username=username))
    elif auth_result is False:
        return "Password incorrect. Please try again."
    else:
        return "User not found. Please register first."

@login_bp.route('/signup', methods=['GET'])
def signup():
    user = request.args.get('user')
    # print(user)
    return render_template('signup.html', user = user)

@login_bp.route('/signup_submit', methods=['POST'])
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