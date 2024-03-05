from flask import Blueprint, render_template, session, request
# import psycopg2
from backend.database import getTestNumberData, add_questions_to_database, add_subject_to_table, get_que_no_from_table_number,check_details_to_update_table, show_users_data

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/<username>')
def index(username):
    if 'username' in session:
        # print(getTestNumberData())
        # index = 0  # Set the initial value of index
        return render_template('admin_side_pages/admin_main.html', username = username)
    else:
        return redirect(url_for('login.index'))

    

"""
    box [ show table -> test_number ]
    another box [
        form::
        Subject:
        Test_no:
        Test_id:
                    submit -> insert into test_number (dataset)
    ]
"""
@admin_bp.route('/view_data_admin/<username>', methods=['GET'])
def view_data_admin(username):
    # username = request.args.get('username')
    data = show_users_data('admin', username)
    # print(data)
    return render_template('admin_side_pages/view_data_admin.html', row_data = data, username = username)
   

@admin_bp.route('/add_subject', methods=['GET'])
def add_subject():
    username = request.args.get('username')
    return render_template('admin_side_pages/add_subject.html', data = getTestNumberData(), username = username)
   

@admin_bp.route('/add_questions', methods=['GET'])
def add_questions_get():
    test_id = request.args.get('test_id')
    username = request.args.get('username')
    #function in Database to add new subject in the database.
    if(request.args.get('submit_type') == 'update'):
        if(check_details_to_update_table(request.args)):
            q_n = get_que_no_from_table_number(test_id)
            return render_template('admin_side_pages/add_questions.html', test_id = test_id, question_number = q_n, username = username )

        return "incorrect details to Update table, try again, or create new table"
    else:
        if(add_subject_to_table(request.args)):
            q_n = get_que_no_from_table_number(test_id)

            return render_template('admin_side_pages/add_questions.html', test_id = test_id, question_number = q_n, username = username )
        else:
            return "unable to add data to the test_number table "
            # return redirect(url_for('admin.index'))

@admin_bp.route('/add_questions', methods=['POST'])
def add_questions():
    if(add_questions_to_database(request.form)):
        test_id = request.form['test_id']
        q_n = get_que_no_from_table_number(test_id)
        username = request.form['username']
        # print(request.form)

        # question_number = 0 
        return render_template('admin_side_pages/add_questions.html', test_id = test_id, question_number = q_n, username = username )
    else:
        return "Unable to add questions to database, Go back and try again"

            
       

    


