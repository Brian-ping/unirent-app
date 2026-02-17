from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from app.controllers.auth_controller import AuthController
from functools import wraps

auth_routes = Blueprint('auth', __name__)

def login_required_custom(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Store the current URL to redirect back after login
            session['next_url'] = request.url
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        contact_number = request.form.get('contact_number')
        id_number = request.form.get('id_number')
        password = request.form.get('password')

        if AuthController.register(full_name, email, contact_number, id_number, password):
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Email already exists. Please login or use a different email.', 'error')
    return render_template('register.html')

@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    # Get the next URL from query parameters (where to redirect after login)
    next_url = request.args.get('next')
    if next_url:
        session['next_url'] = next_url  # Store in session for after login
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Get both user and message from the tuple
        user, message = AuthController.login(email, password)
        
        if user:
            # Store user ID in session
            session['user_id'] = str(user['_id'])
            session['user_email'] = user.get('email', '')
            flash('Login successful!', 'success')
            
            # Check if there's a next URL to redirect to
            next_url = session.pop('next_url', None)
            if next_url:
                return redirect(next_url)
            return redirect(url_for('main.home'))
        
        flash(message, 'error')
    
    return render_template('login.html')

@auth_routes.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        if AuthController.reset_password(email):
            flash('Reset link sent to your email. Check your inbox.', 'success')
        else:
            flash('Email not found. Please check your email or register.', 'error')
    return render_template('reset_password.html')

@auth_routes.route('/new_password', methods=['GET', 'POST'])
def new_password():
    token = request.args.get('token')
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        if AuthController.update_password(token, new_password):
            flash('Password updated successfully! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid or expired token. Please request a new reset link.', 'error')
    return render_template('new_password.html', token=token)

@auth_routes.route('/logout')
def logout():
    session.pop('user_id', None)  # Clear user session
    session.pop('user_email', None)  # Clear email as well
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))