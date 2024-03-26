from flask import Blueprint, render_template, session, request, redirect, url_for
from backend.database import view_profile_data, update_profile_database

profile_bp = Blueprint('profile', __name__)

images_folder = "/user_images"  # Replace with your images folder path

@profile_bp.route('/view_profile/<username>')
def index(username):
    # return "success"
    # global user_type
    # print(session['username'])

    # user = session['user']
    # print("usr ty 1 : " + user_type)
    data = view_profile_data(username)
    print(data)
    return render_template('profiles/view_profile.html', data = data, username = username)
    
@profile_bp.route('/edit_profile', methods=['GET'])
def edit_profile():
    # print("usr ty 2 : " + user_type)
    # user = session['user']
    username = session['username']
    data = view_profile_data(username)
    return render_template('profiles/edit_profile.html',data = data, username = username)

@profile_bp.route('/update_profile', methods=['POST'])
def update_profile():
    # global user_type
    # user = session['user']
    username = session['username']

    # image_file = request.files["profile_pic"]
    # image_path = request.form['image_path']
    # print(request.files)  # Added for debugging

    # if username and image_file:
    #     # print("enter this if condition")
    #     # Construct filename using username and extension
    #     filename = f"{username}.jpg"  # Adjust extension as needed
    #     # Construct image path only if there's an image file
    #     image_path = os.path.join(images_folder, filename)

    #     # Save image
    #     image_file.save(image_path)
    # print("usr ty 3 : " + user_type)
    # print("user type : " + user_type + " username  :" + username + "request.form : ")
    update_profile_database( username, request.form)
    data = view_profile_data(username)
    # return redirect(url_for('profile.index', username=username))
    return render_template('profiles/view_profile.html', data = data, username = username)
