from flask import Blueprint, render_template, session, redirect, url_for

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html', role=session.get('role'))

@dashboard_bp.route('/')
def home():
    return redirect(url_for('dashboard.dashboard'))
