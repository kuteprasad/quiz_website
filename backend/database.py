import psycopg2

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