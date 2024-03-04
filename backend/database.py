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
        conn.commit()  # Commit the transaction
        conn.close()

        if(rows[0][0] == 1):
            return True
        elif(rows[0][0] == 0):
            return None
    except Exception as e:
        print("Error occurred while inserting data:", e)
        return False

