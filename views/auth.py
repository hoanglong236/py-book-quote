from flask import Blueprint, render_template, request, redirect, url_for

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login logic...
        return redirect(url_for('home.index'))

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Handle register logic...
        username = request.form.get('username')
        password = request.form.get('password')

        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')