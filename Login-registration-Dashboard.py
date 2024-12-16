from flask import Flask, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template_string
import os

# Flask App Setup
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for session management
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database Initialization
db = SQLAlchemy(app)

# User Model for Registration
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

# HTML Templates (Binance-like UI)

# Registration Page Template
register_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Register | EMR System</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #121212; color: #fff; text-align: center; }
        .container { margin-top: 50px; width: 350px; margin: auto; background: #1e1e1e; padding: 20px; border-radius: 10px; }
        input { width: 90%; padding: 10px; margin: 10px; border: none; border-radius: 5px; }
        button { width: 95%; padding: 10px; background-color: #f0b90b; color: #121212; border: none; border-radius: 5px; cursor: pointer; }
        a { color: #f0b90b; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Create an Account</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required><br>
            <input type="email" name="email" placeholder="Email" required><br>
            <input type="password" name="password" placeholder="Password" required><br>
            <button type="submit">Register</button>
        </form>
        <p>Already have an account? <a href="{{ url_for('login') }}">Login here</a></p>
    </div>
</body>
</html>
"""

# Login Page Template
login_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Login | EMR System</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #121212; color: #fff; text-align: center; }
        .container { margin-top: 50px; width: 350px; margin: auto; background: #1e1e1e; padding: 20px; border-radius: 10px; }
        input { width: 90%; padding: 10px; margin: 10px; border: none; border-radius: 5px; }
        button { width: 95%; padding: 10px; background-color: #f0b90b; color: #121212; border: none; border-radius: 5px; cursor: pointer; }
        a { color: #f0b90b; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Login</h2>
        <form method="POST">
            <input type="email" name="email" placeholder="Email" required><br>
            <input type="password" name="password" placeholder="Password" required><br>
            <button type="submit">Login</button>
        </form>
        <p>Don't have an account? <a href="{{ url_for('register') }}">Register here</a></p>
    </div>
</body>
</html>
"""

# Dashboard Page Template
dashboard_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Dashboard | EMR System</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #121212; color: #fff; text-align: center; margin-top: 50px; }
        a { color: #f0b90b; text-decoration: none; font-size: 20px; }
    </style>
</head>
<body>
    <h1>Welcome to the EMR Dashboard, {{ username }}</h1>
    <p>You are successfully logged in!</p>
    <a href="{{ url_for('logout') }}">Logout</a>
</body>
</html>
"""

# Routes

# Home Page
@app.route('/')
def home():
    return redirect(url_for('login'))

# Registration Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))

        # Add new user
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template_string(register_template)

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials, please try again.', 'error')
    return render_template_string(login_template)

# Dashboard Page
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template_string(dashboard_template, username=session['username'])

# Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# Run the App
if __name__ == '__main__':
    if not os.path.exists("users.db"):
        with app.app_context():
            db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
