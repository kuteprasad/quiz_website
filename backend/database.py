from flask import session
import psycopg2
import hashlib  # For generating a random salt
import subprocess
import os
from datetime import date, datetime

def connect_to_db():
    db_password = os.environ.get("DB_PASSWORD")
    if not db_password:
        raise ValueError("DB_PASSWORD environment variable not set")

    conn = psycopg2.connect(
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=db_password,
        host=os.environ.get("DB_HOST"),
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


def generate_random_salt():
    return os.urandom(32)  # Generate a random salt


# create a password hash
def hash_password(password, salt):
    hashed_password = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 100000
    )
    return hashed_password.hex()


def secure_compare(val1, val2):
    """
    Performs a constant-time comparison to avoid timing attacks.

    Args:
        val1 (str): The first value to compare.
        val2 (str): The second value to compare.

    Returns:
        bool: True if the values are equal, False otherwise.
    """

    if len(val1) != len(val2):
        return False
    result = 0
    for x, y in zip(val1, val2):
        result |= ord(x) ^ ord(y)
    return result == 0  # Constant time comparison


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
                image_path VARCHAR(255) DEFAULT '/user_images/githublogo.png'::VARCHAR, -- Adjust size if needed
                password_salt BYTEA NOT NULL,
                password_hash BYTEA NOT NULL -- Use secure password hashing (pgcrypto recommended)
            );""",
            """CREATE TABLE IF NOT EXISTS test_details (
                test_id SERIAL PRIMARY KEY,
                subject VARCHAR(50) NOT NULL,
                test_no INTEGER NOT NULL,
                test_duration INTEGER NOT NULL,
                total_marks INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                UNIQUE (subject, test_no)
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
            );""",
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
            salt = generate_random_salt()
            hashed_password = hash_password("1234", salt)

            query = f"""
                INSERT INTO accounts (user_id, username, first_name, last_name, email, phone_number, user_type, password_salt, password_hash) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(
                query,
                (
                    1,
                    "prasad",
                    "Prasad",
                    "Kute",
                    "prasadkute0708@gmail.com",
                    "+917558750366",
                    "student",
                    salt,
                    hashed_password,
                ),
            )
            print("line 171: accounts inserted, db.py")

        if is_table_empty("test_details"):
            query = f"""
                INSERT INTO test_details ( subject, test_no, test_duration, total_marks, total_questions)
                VALUES ( %s, %s, %s, %s, %s);
            """
            cursor.execute(query, ("General Knowledge", 1, 60, 10, 2))
            print("line 175: test_details inserted, db.py")

        if is_table_empty("test_data"):
            query = f"""
                INSERT INTO test_data ( test_id, question_no, question, option1, option2, option3, option4, correct_answer)
                VALUES ( %s, %s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(
                query,
                (
                    1,
                    1,
                    "What is Capital of India?",
                    "New Delhi",
                    "Mumbai",
                    "Pune",
                    "Junnar",
                    "New Delhi",
                ),
            )
            cursor.execute(
                query,
                (
                    1,
                    2,
                    "What is Capital of Maharashtra?",
                    "New Delhi",
                    "Mumbai",
                    "Pune",
                    "Junnar",
                    "Mumbai",
                ),
            )

        if is_table_empty("user_data"):
            query = f"""
                INSERT INTO user_data (user_id, test_id, score, time_required, date_stamp, time_stamp)
                  VALUES (%s, %s, %s, %s, %s, %s);
            """
            cursor.execute(query, (1, 1, 8, 40, "2024-03-25", "10:30:00"))
            # print("line 175: test_details inserted, db.py")

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


# def insert_user( username, first_name, last_name, email, phone_number, user, password):

#     try:
#         conn = connect_to_db()
#         cursor = conn.cursor()

#         salt = generate_random_salt()
#         hashed_password = hash_password(password, salt)
#         query = f"""
#             INSERT INTO accounts (username, first_name, last_name, email, phone_number, user, password_salt , password_hash)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
#         """
#         cursor.execute(query, (username, first_name, last_name, email, phone_number, user, salt, hashed_password))
#         conn.commit()
#         print(f"User '{username}' created successfully.")
#     except Exception as e:
#         print(f"Error creating user: {e}")
#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()

# def insert_test_details(subject, test_no, test_duration, total_marks, total_questions):
#     try:
#         conn = connect_to_db()
#         cursor = conn.cursor()

#         query = f"""
#             INSERT INTO test_details (subject, test_no, test_duration, total_marks, total_questions)
#             VALUES (%s, %s, %s, %s, %s);
#         """
#         cursor.execute(query, (subject, test_no, test_duration, total_marks, total_questions))
#         conn.commit()
#         print(f"Test details for '{subject}' created successfully.")
#     except Exception as e:
#         print(f"Error creating test details: {e}")
#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()

# def insert_test_data(test_id, question_no, question, option1, option2, option3, option4, correct_answer):
#     try:
#         conn = connect_to_db()
#         cursor = conn.cursor()

#         query = f"""
#             INSERT INTO test_data (test_id, question_no, question, option1, option2, option3, option4, correct_answer)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
#         """
#         cursor.execute(query, (test_id, question_no, question, option1, option2, option3, option4, correct_answer))
#         conn.commit()
#         print(f"Test data for question {question_no} created successfully.")
#     except Exception as e:
#         print(f"Error creating test data: {e}")
#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()


def authenticate_user(user, username, password):

    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        query = f"SELECT password_salt, password_hash FROM accounts WHERE username = %s AND user_type = %s"
        cursor.execute(query, (username, user))
        row = cursor.fetchone()

        stored_salt = row[0]  # Assuming stored salt is the first element in the row
        stored_hash = row[1]  # Assuming stored hash is the second element in the row

        hashed_password = hash_password(password, stored_salt)

        # print_password = stored_hash.tobytes().decode('utf-8')  # Assuming stored_hash is a tuple
        if row:
            # # stored_password = row[0]
            # print("stored_password  --> " + print_password)
            # print("hashed_password  --> " + hashed_password)
            if secure_compare(stored_hash, hashed_password):
                return True  # Passwords match
            else:
                return False  # Incorrect password
        else:
            return None  # User not found

    except Exception as e:
        print(f"Error authenticating user: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()


def signup_user(form_data, image_path):

    user = session["user"]  # Assuming user type is retrieved from form data
    username = form_data["username"]
    first_name = form_data["first_name"]
    last_name = form_data["last_name"]
    email = form_data["email"]
    phone_number = form_data["phone_number"]
    password = form_data["password"]
    if image_path == False:
        image_path = "/user_images/githublogo.png"

    # Generate a random salt for password hashing
    salt = generate_random_salt()

    # Hash the password using a secure algorithm (e.g., bcrypt)
    hashed_password = hash_password(password, salt)

    # Establish a connection to the database
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        # Execute SQL INSERT query with parameterized query to prevent SQL injection
        query = """
            INSERT INTO accounts (user_type, username, first_name, last_name, email, phone_number, image_path, password_salt, password_hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                user,
                username,
                first_name,
                last_name,
                email,
                phone_number,
                image_path,
                salt,
                hashed_password,
            ),
        )

        # Commit the transaction
        conn.commit()

        print("User created successfully!")
        # return "User created successfully!"  # Or a success message

    except (psycopg2.Error, Exception) as e:
        # Handle potential database errors and generic exceptions
        # Check if the error is due to a duplicate key violation
        if e.pgcode and e.pgcode == "23505":
            # If username already exists, return "User already exists"
            return "User already exists. Please choose a different username."
        else:
            # If the error is not a duplicate key violation, print the error
            print("Error occurred:", e)
            return "An error occurred. Please try again later."

    finally:
        # Ensure proper connection closure even on exceptions
        if conn:
            cursor.close()
            conn.close()


def view_profile_data(username):

    # Determine the appropriate table name based on user type
    # table_name = return_table_name(user)

    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        # Use a parameterized query to prevent SQL injection
        query = f"SELECT * FROM accounts WHERE username = %s;"
        cursor.execute(query, (username,))

        row = cursor.fetchone()

        if row:
            return row  # Return the user profile data if found
        else:
            return None  # Indicate that the user was not found

    except (psycopg2.Error, Exception) as e:
        print(f"Error retrieving profile data: {e}")
        return None  # Indicate an error occurred

    finally:
        if conn:
            cursor.close()
            conn.close()  # Ensure proper connection closure


def update_profile_database(username, form_data):

    # Validate user input (optional but recommended)
    # ... (implement validation logic here)

    # Extract data from the form
    new_data = {
        key: value
        for key, value in form_data.items()
        if key in ("first_name", "last_name", "phone_number", "email")
    }

    # Generate a random salt for password hashing (if updating password)
    if "password" in form_data:
        salt = generate_random_salt()
        hashed_password = hash_password(form_data["password"], salt)
        new_data["password_salt"] = salt
        new_data["password_hash"] = hashed_password
    else:
        # Maintain existing password hash (assuming separate logic for password change)
        pass

    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        # Use parameterized queries to prevent SQL injection
        update_clauses = []
        for key, value in new_data.items():
            update_clauses.append(f"{key} = %s")

        # Combine update clauses with comma separators
        update_string = ", ".join(update_clauses)

        query = f"""
            UPDATE accounts
            SET {update_string}
            WHERE username = %s;
        """
        parameters = tuple(new_data.values()) + (username,)

        cursor.execute(query, parameters)

        conn.commit()

        print("Profile updated successfully!")  # Or a success message

    except (psycopg2.Error, Exception) as e:
        print(f"Error updating profile: {e}")
        return "An error occurred. Please try again later."  # Or an error message

    finally:
        if conn:
            cursor.close()
            conn.close()



def get_test_data(id):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        # Use parameterized queries to prevent SQL injection
        query = "SELECT * FROM test_data WHERE test_id = %s"
        cursor.execute(query, (id,))

        rows = cursor.fetchall()

        if rows:
            return rows  # Return the test data if found
        else:
            return None  # Indicate that the test data is not found

    except (psycopg2.Error, Exception) as e:
        print(f"Error retrieving test data: {e}")
        return None  # Indicate an error occurred

    finally:
        if conn:
            cursor.close()
            conn.close()  # Ensure proper connection closure

def get_test_id(form_data):
    subject = form_data['subject']
    test_no = form_data['test_no']
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        # Use parameterized queries to prevent SQL injection
        query = "SELECT * FROM test_details WHERE subject = %s AND test_no = %s"
        cursor.execute(query, (subject,test_no))

        rows = cursor.fetchone()[0]  # Assuming a single value is returned

        if rows:
            return rows  # Return the test id if found
        else:
            return None  # Indicate that the test id is not found

    except (psycopg2.Error, Exception) as e:
        print(f"Error retrieving test data: {e}")
        return None  # Indicate an error occurred

    finally:
        if conn:
            cursor.close()
            conn.close()  # Ensure proper connection closure

def get_test_details():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        # Use parameterized queries to prevent SQL injection (even for simple queries)
        query = "SELECT * FROM test_details ORDER BY subject ASC"
        cursor.execute(query)  # Parameters not required in this case

        rows = cursor.fetchall()

        return rows  # Return the test numbers data

    except (psycopg2.Error, Exception) as e:
        print(f"Error retrieving test numbers data: {e}")
        return None  # Indicate an error occurred

    finally:
        if conn:
            cursor.close()
            conn.close()  # Ensure proper connection closure


def add_test_details(form_data):
    conn = connect_to_db()
    cursor = conn.cursor()
        # Extract data from the form
    subject = form_data["subject"]
    test_duration = int(form_data["test_duration"])
    total_marks = int(form_data["total_marks"])

        # test_duration = 60
        # int(
        #     form_data["test_duration"]
        # )  # Assuming test duration is an integer
        # total_marks = 10
        # int(
        #     form_data["total_marks"]
        # )  # Assuming total marks is an integer
    total_questions = 0
        #     form_data["total_questions"]
        # )  # Assuming total questions is an integer
    try:

        # Retrieve the latest test number (assuming test_no is auto-incrementing)
        query = "SELECT MAX(test_no) FROM test_details WHERE subject = %s"
        cursor.execute(query, (subject,))
        latest_test_no = cursor.fetchone()[0]
        # print(latest_test_no)  
        # Assuming a single value is returned

        # If no test exists yet, start with test_no 1
        if latest_test_no is None:
            new_test_no = 1
        else:
            new_test_no = latest_test_no + 1

        # Use parameterized queries to prevent SQL injection
        query = """ INSERT INTO test_details (subject, test_no, test_duration, total_marks, total_questions) VALUES (%s, %s, %s, %s, %s) """

        parameters = (subject, new_test_no, test_duration, total_marks,total_questions)

        cursor.execute(query, parameters)
        conn.commit()
 
        return True  
        #Indicate successful insertion

    except (psycopg2.Error, Exception) as e:
        print(f"Error adding test details: {e}")
        return False  # Indicate an error occurred

    finally:
        if conn:
            cursor.close()
            conn.close()  # Ensure proper connection closure

def get_question_number_from_test_details(test_id):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        # Use parameterized queries to prevent SQL injection
        query = "SELECT total_questions FROM test_details WHERE test_id = %s"
        cursor.execute(query, (test_id,))

        row = cursor.fetchone()

        if row:
            # Increment the total questions if a test is found
            return row[0] + 1
        else:
            return None  # Indicate that the test ID is not found

    except (psycopg2.Error, Exception) as e:
        print(f"Error getting question number: {e}")
        return None  # Indicate an error occurred

    finally:
        if conn:
            cursor.close()
            conn.close()  # Ensure proper connection closure


def add_questions_to_database(form_data):
    test_id = int(form_data["test_id"])
    question_no = get_question_number_from_test_details(test_id)  
    # Use the correct function

    try:
        # Extract data from the form
        question = form_data["question"]
        option1 = form_data["option1"]
        option2 = form_data["option2"]
        option3 = form_data["option3"]
        option4 = form_data["option4"]
        correct_answer = form_data["correct_answer"]

        conn = connect_to_db()
        cursor = conn.cursor()

        # Use parameterized queries to prevent SQL injection
        query = """
            INSERT INTO test_data (test_id, question_no, question, option1, option2, option3, option4, correct_answer)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        parameters = (
            test_id,
            question_no,
            question,
            option1,
            option2,
            option3,
            option4,
            correct_answer,
        )

        cursor.execute(query, parameters)

        query = "UPDATE test_details SET total_questions = %s WHERE test_id = %s"  # Use correct table name
        cursor.execute(query, (question_no, test_id))

        conn.commit()

        return True  # Indicate successful insertion

    except (psycopg2.Error, Exception) as e:
        print(f"Error adding question: {e}")
        return False  # Indicate an error occurred

    finally:
        if conn:
            cursor.close()
            conn.close()  # Ensure proper connection closure


def check_details_to_update_table(form_data):
    try:
        subject = form_data["subject"]
        test_no = form_data["test_no"]
        # test_id = int(form_data['test_id'])

        conn = connect_to_db()
        cursor = conn.cursor()

        # Use parameterized queries to prevent SQL injection
        query = "SELECT COUNT(*) FROM test_details WHERE (subject, test_no) = (%s, %s)"  # Use correct table name
        cursor.execute(query, (subject, test_no))

        row = cursor.fetchone()

        if row[0] == 1:
            return True  # Details exist for update
        else:
            return False  # Details don't exist

    except (psycopg2.Error, Exception) as e:
        print(f"Error checking details: {e}")
        return False  # Indicate an error occurred

    finally:
        if conn:
            cursor.close()
            conn.close()  # Ensure proper connection closure

def add_users_data(username, form_data):
    
    today_date = date.today().strftime('%Y-%m-%d')  # Format: YYYY-MM-DD
    current_time = datetime.now().strftime('%H:%M:%S')  # Format: HH:MM:SS

    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        query = "SELECT user_id FROM accounts WHERE username = %s;"
        cursor.execute(query, (username,))
        user_id = cursor.fetchone()[0]

        query = "INSERT INTO user_data (user_id, test_id, score, time_required, date_stamp, time_stamp ) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (user_id, form_data['test_id'], form_data['total_score'], form_data['time_taken'], today_date, current_time ))

        conn.commit()

    except (psycopg2.Error, Exception) as e:
        print(f"Error fetching user data: {e}")
        return None  # Indicate an error occurred

    finally:
        if conn:
            cursor.close()
            conn.close()  # Ensure proper connection closure

def show_users_data(user, username, test_id=0):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        if user == "admin":
            # Fetch all data from users_data table
            query = """SELECT ROW_NUMBER() OVER (ORDER BY ud.id) AS serial_no,
                u.username,
                u.first_name,
                u.last_name,
                td.subject,
                td.test_no,
                ud.score ,
                td.total_marks,
                ud.time_required,
                td.test_duration,
                ud.date_stamp,
                ud.time_stamp
            FROM user_data ud
            INNER JOIN accounts u ON ud.user_id = u.user_id  -- Use 'u' for accounts
            INNER JOIN test_details td ON ud.test_id = td.test_id;  -- Use 'td' for test_details"""

            cursor.execute(query)
        else:
            query = "SELECT user_id FROM accounts WHERE username = %s;"
            cursor.execute(query, (username,))
            user_id = cursor.fetchone()[0]
            if test_id == 0:
                # Fetch complete data of specific user
                query = "SELECT * FROM user_data WHERE user_id = %s"
                parameters = (user_id,)
            else:
                # Fetch user data of specific test ID
                query = "SELECT * FROM user_data WHERE user_id = %s AND test_id = %s"
                parameters = (user_id, test_id)
            cursor.execute(query, parameters)  # Use parameterized queries

        rows = cursor.fetchall()

        return rows  # Return the fetched data

    except (psycopg2.Error, Exception) as e:
        print(f"Error fetching user data: {e}")
        return None  # Indicate an error occurred

    finally:
        if conn:
            cursor.close()
            conn.close()  # Ensure proper connection closure
