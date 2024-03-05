from flask import Blueprint, render_template, session, request, redirect, url_for
from backend.database import view_profile_data, updata_profile_database

profile_bp = Blueprint('profile', __name__)

# user_type = ''

@profile_bp.route('/view_profile/<username>')
def index(username):
    # return "success"
    # global user_type
    user_type = request.args.get('user_type')
    # print("usr ty 1 : " + user_type)
    data = view_profile_data(user_type, username)
    # print(data)
    return render_template('profiles/view_profile.html', data = data, username = username, user_type = user_type)
    
@profile_bp.route('/edit_profile/<username>', methods=['GET'])
def edit_profile(username):
    user_type = request.args.get('user_type')
    # print("usr ty 2 : " + user_type)

    data = view_profile_data(user_type, username)
    return render_template('profiles/edit_profile.html',data = data, username = username , user_type = user_type)

@profile_bp.route('/update_profile/<username>', methods=['POST'])
def update_profile(username):
    # global user_type
    user_type = request.form['user_type']
    # print("usr ty 3 : " + user_type)

    # print("user type : " + user_type + " username  :" + username + "request.form : ")
    updata_profile_database(user_type, username, request.form)
    data = view_profile_data(user_type, username)
    # return redirect(url_for('profile.index', username=username))
    return render_template('profiles/view_profile.html', data = data, username = username , user_type = user_type)
