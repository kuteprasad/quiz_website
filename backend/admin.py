from flask import Blueprint, render_template, session, request
# import psycopg2
from backend.database import get_test_details, add_questions_to_database, add_test_details, get_question_number_from_test_details, check_details_to_update_table, show_users_data, get_test_id

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
def index():
    if 'username' in session:
        # print(getTestNumberData())
        # index = 0  # Set the initial value of index
        return render_template('admin_side_pages/admin_main.html', username = session['username'])
    else:
        return redirect(url_for('login.index'))

@admin_bp.route('/users_list', methods=['GET'])
def users_list():
    #logic to return all added users list... 
    #data to returned sr, pic, username, first, last, mob, email, total test given(count) 
    return render_template('empty.html', data = "Route not defined in Admin.py (/users_list) ")
    
@admin_bp.route('/users_test_data', methods=['GET'])
def users_test_data():
    username = session['username']
    data = show_users_data('admin', username)
    # print(data)
    return render_template('admin_side_pages/users_test_data.html', row_data = data, username = username)
   

@admin_bp.route('/view_subject', methods=['GET'])
def view_subject():
    # username = request.args.get('username')
    return render_template('admin_side_pages/view_subject.html', data = get_test_details(), username = session['username'])
   

@admin_bp.route('/add_questions', methods=['GET'])
def add_questions_get():
    test_id = get_test_id(request.args)
    username = session['username']
    #function in Database to add new subject in the database.
    if(request.args.get('submit_type') == 'update'):
        if(check_details_to_update_table(request.args)):
            
            
            q_n = get_question_number_from_test_details(test_id)
            return render_template('admin_side_pages/add_questions.html', test_id = test_id, question_no = q_n, username = username )

        return "incorrect details to Update table, try again, or create new table"
    else:
        if(add_test_details(request.args)):

            return render_template('admin_side_pages/add_questions.html', test_id = test_id, question_no = 1, username = username)
        else:
            return "unable to add data to the test_details table"
            # return redirect(url_for('admin.index'))

@admin_bp.route('/add_questions', methods=['POST'])
def add_questions():
    if(add_questions_to_database(request.form)):
        test_id = request.form['test_id']
        q_n = get_question_number_from_test_details(test_id)
        username = session['username']

        # question_number = 0 
        return render_template('admin_side_pages/add_questions.html', test_id = test_id, question_no = q_n, username = username )
    else:
        return "Unable to add questions to database, Go back and try again"
