import psycopg2
import hashlib  # For generating a random salt
import subprocess
import os


DB_NAME = 'quiz'
DB_USER = 'postgres'
DB_PASSWORD = 'india@11'
DB_HOST = 'localhost'

def connect_to_db():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
    )
    return conn

def enable_pgcrypto(conn):
    
    """
    Attempts to enable the pgcrypto extension in the connected PostgreSQL database.

    Args:
        conn: A psycopg2 connection object.

    Returns:
        True if the extension was successfully enabled, False otherwise.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
        conn.commit()
        return True
    except Exception as e:
        print(f"Error enabling pgcrypto extension: {e}")
        return False

# create a password hash 
def hash_password(password):
    salt = os.urandom(32)  # Generate a random salt
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return hashed_password.hex()

def setup_initial_tables():
    
    """
    Establishes a connection to the database, creates the necessary tables if they don't exist,
    and commits the changes.

    Returns:
        None on success, or an exception object if an error occurs.
    """

    try:
        # Replace with your actual database connection logic (e.g., using psycopg2)
        conn = connect_to_db()
        cursor = conn.cursor()

        # Attempts to enable the pgcrypto extension in the connected PostgreSQL database.
        success = enable_pgcrypto(conn)
        if success:
            print("pgcrypto extension enabled successfully.")
        else:
            print("Failed to enable pgcrypto extension.")


        # Create tables (if not exist)
        create_table_queries = [
            """CREATE TABLE IF NOT EXISTS accounts (
                user_id SERIAL PRIMARY KEY,
                user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('student', 'teacher', 'admin', 'guest')),
                username VARCHAR(50) NOT NULL UNIQUE,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                phone_number VARCHAR(20) NOT NULL,
                password_hash BYTEA NOT NULL -- Use secure password hashing (pgcrypto recommended)
            );""",

            """CREATE TABLE IF NOT EXISTS test_details (
                test_id SERIAL PRIMARY KEY,
                subject VARCHAR(50) NOT NULL,
                test_no INTEGER NOT NULL,
                test_duration INTEGER NOT NULL,
                total_marks INTEGER NOT NULL,
                total_questions INTEGER NOT NULL
            );""",

            """CREATE TABLE IF NOT EXISTS test_data (
                id SERIAL PRIMARY KEY,
                test_id INTEGER NOT NULL,
                FOREIGN KEY (test_id) REFERENCES test_details(test_id) ON DELETE CASCADE,
                question_no INTEGER NOT NULL,
                question TEXT NOT NULL,
                option1 TEXT NOT NULL,
                option2 TEXT NOT NULL,
                option3 TEXT NOT NULL,
                option4 TEXT NOT NULL,
                correct_answer TEXT NOT NULL
            );""",

            """CREATE TABLE IF NOT EXISTS user_data (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES accounts(user_id) ON DELETE CASCADE,
                test_id INTEGER NOT NULL,
                FOREIGN KEY (test_id) REFERENCES test_details(test_id) ON DELETE CASCADE,
                score INTEGER NOT NULL,
                time_required INTEGER NOT NULL,
                date_stamp DATE NOT NULL,
                time_stamp TIME WITHOUT TIME ZONE NOT NULL
            );"""
        ]

        for query in create_table_queries:
            cursor.execute(query)

        # Commit the transaction
        conn.commit()
        print("Tables created successfully (if they didn't already exist).")


    except Exception as e:
        # Roll back any changes if an error occurs
        conn.rollback()
        print("Error while creating tables:", e)
        return e
    finally:
        # Close the cursor and database connection (ensure they're closed even on exceptions)
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return None  # Indicate successful execution

def insert_initial_data():
    """
    Inserts initial data into the database tables if they are empty, using secure password hashing.

    This function connects to the database, checks if each table is empty, and inserts
    sample data if the table is empty. It uses secure password hashing for the user account.

    Raises an exception if there's an error connecting to the database or executing queries.
    """

    try:
        # Replace with your actual database connection details
        conn = connect_to_db()
        cursor = conn.cursor()

        # Define functions to check if tables are empty (replace with your actual table names)
        def is_table_empty(table_name):
            query = f"SELECT EXISTS (SELECT 1 FROM {table_name});"
            cursor.execute(query)
            return not cursor.fetchone()[0]

        # Check if tables are empty and insert data if necessary
        if is_table_empty("accounts"):
            hashed_password = hash_password("password123")
            query = f"""
                INSERT INTO accounts (username, first_name, last_name, email, phone_number, user_type, password_hash)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(query, ("john_doe", "John", "Doe", "john.doe@example.com", "+1234567890", "student", hashed_password))

        if is_table_empty("test_details"):
            query = f"""
                INSERT INTO test_details (subject, test_no, test_duration, total_marks, total_questions)
                VALUES (%s, %s, %s, %s, %s);
            """
            cursor.execute(query, ("Mathematics", 1, 60, 100, 20))

        if is_table_empty("test_data"):
            query = f"""
                INSERT INTO test_data (test_id, question_no, question, option1, option2, option3, option4, correct_answer)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(query, (1, 1, "What is 2 + 2?", "1", "3", "4", "5", "4"))

        conn.commit()
        print("Initial data inserted successfully (if tables were empty).")

    except (Exception, psycopg2.Error) as error:
        print("Error while inserting initial data:", error)
        raise  # Re-raise the exception for further handling

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def insert_user( username, first_name, last_name, email, phone_number, user_type, password):

    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        hashed_password = hash_password(password)
        query = f"""
            INSERT INTO accounts (username, first_name, last_name, email, phone_number, user_type, password_hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(query, (username, first_name, last_name, email, phone_number, user_type, hashed_password))
        conn.commit()
        print(f"User '{username}' created successfully.")
    except Exception as e:
        print(f"Error creating user: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def insert_test_details(subject, test_no, test_duration, total_marks, total_questions):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        query = f"""
            INSERT INTO test_details (subject, test_no, test_duration, total_marks, total_questions)
            VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(query, (subject, test_no, test_duration, total_marks, total_questions))
        conn.commit()
        print(f"Test details for '{subject}' created successfully.")
    except Exception as e:
        print(f"Error creating test details: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def insert_test_data(test_id, question_no, question, option1, option2, option3, option4, correct_answer):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        query = f"""
            INSERT INTO test_data (test_id, question_no, question, option1, option2, option3, option4, correct_answer)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(query, (test_id, question_no, question, option1, option2, option3, option4, correct_answer))
        conn.commit()
        print(f"Test data for question {question_no} created successfully.")
    except Exception as e:
        print(f"Error creating test data: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def return_table_name(user):
    if user == 'admin':
        return "accounts_admin"
    else:
        return "accounts"

def authenticate_user(user, username, password):
    table_name = return_table_name(user)
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


# Get form data
def signup_user(form_data):

    user = form_data['user']
    username = form_data['username']
    email = form_data['email']
    password = form_data['password']

    table_name = return_table_name(user)

        # Establish a connection to the database
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        # Execute SQL INSERT query to insert user data into the database
        query = f"INSERT INTO {table_name} (username, email, password) VALUES (%s, %s, %s);"
        cursor.execute(query, ( username, email, password ))
        
        # Commit the transaction
        conn.commit()
        
        # Close the cursor and database connection
        cursor.close()
        conn.close()
    
    except Exception as e:
        return e

def view_profile_data(user_type, username):
    table_name = return_table_name(user_type)
    conn = connect_to_db()
    cursor = conn.cursor()
    query = f"SELECT * FROM {table_name} WHERE username = %s"
    cursor.execute(query, (username,))
    row = cursor.fetchone()
    conn.close()
    # print(row[0])
    return row

def updata_profile_database(user_type, username, form_data):
    table_name = return_table_name(user_type)

    new_username = form_data['username']
    new_email = form_data['email']
    new_password = form_data['password']

    conn = connect_to_db()
    cursor = conn.cursor()
    query = f"UPDATE {table_name} SET username = %s, email = %s, password = %s WHERE username = %s"
    cursor.execute(query, (new_username, new_email, new_password, username))
    conn.commit()  # Commit the transaction after executing the update query
    conn.close()


def getTestData(test_number):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM test_data WHERE test_id = %s", (test_number,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def getTestNumberData():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM test_number ORDER BY subject ASC;")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_subject_to_table(form_data):
    try:
        data = (  
            form_data['subject'],
            form_data['test_no'],
            int(form_data['test_id']), 
            0
        )

        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO test_number ( subject, test_no, test_id, total_questions) VALUES %s;", (data,))
        conn.commit()  # Commit the transaction
        conn.close()
        return True
    except Exception as e:
        print("Error occurred while inserting data:", e)
        return False

def get_que_no_from_table_number(test_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    query = f"SELECT total_questions FROM test_number WHERE test_id = {test_id} ;"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    # print(rows)
    return rows[0][0] + 1

def add_questions_to_database(form_data):
    
    test_id = int(form_data['test_id'])
    question_number = get_que_no_from_table_number(test_id) 
    # question_number = get_que_no_from_table_number(244)[0][0] + 1 
    # print(question_number)
    # return False
    try:
        data = (
            int(form_data['test_id']),
            # int(form_data['question_number']),
            question_number,
            form_data['question'],
            form_data['option1'],
            form_data['option2'],
            form_data['option3'],
            form_data['option4'],
            form_data['correct_answer']
        )

        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO test_data (test_id, question_no, question, option_1, option_2, option_3, option_4, correct_option) VALUES %s;", (data,))
        cursor.execute(f"UPDATE test_number SET total_questions = {question_number} WHERE test_id = {test_id};")
        conn.commit()  # Commit the transaction
        conn.close()
        return True
    except Exception as e:
        print("Error occurred while inserting data:", e)
        return False

def check_details_to_update_table(form_data):
    try:
        data = (  
            form_data['subject'],
            form_data['test_no'],
            int(form_data['test_id'])
        )

        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_number WHERE (subject, test_no, test_id) = %s ;", (data,))
        rows = cursor.fetchall()
        

        if(rows[0][0] == 1):
            return True
        elif(rows[0][0] == 0):
            return None
    except Exception as e:
        print("Error occurred while inserting data:", e)
        return False

def show_users_data(user_type='admin', username='prasad', test_id=0):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        if(user_type == 'admin'):
            #return all data in users_data table 
            query = f"SELECT * FROM users_data;"
        else:
            if(test_id == 0):
                #return complete data of specific user:
                query = f"SELECT * FROM users_data WHERE username = '{username}' ;"
            else:
                #return user data of specific test id from users_data table 
                query = f"SELECT * FROM users_data WHERE username = '{username}' AND test_id = {test_id};"
            
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.commit()  # Commit the transaction
        conn.close()
        return rows
    except Exception as e:
        print("Error occurred while inserting data:", e)
        return False

# print(show_users_data('student', 'prasad', 244))