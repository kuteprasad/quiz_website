from flask import Blueprint, render_template, session, request

student_bp = Blueprint('student', __name__)

@student_bp.route('/student/<username>')
def index(username):
    return "success to following route : @student_bp.route('/student/<username>') " 