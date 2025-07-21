from flask import Blueprint, render_template, request, redirect, url_for
from ..models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')


