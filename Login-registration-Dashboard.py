from flask import Flask, request, session, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template_string
from datetime import datetime
import os

# Flask App Setup
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database Initialization
db = SQLAlchemy(app)


# User Roles: Administrator, Doctor, Patient
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, doctor, patient
    doctor_expiry = db.Column(db.DateTime,
                              nullable=True)  # Expiry date for doctors


# Create database tables
with app.app_context():
    db.create_all()
# Create Default Admin Account
with app.app_context():
    if not User.query.filter_by(email="admin@emrsystem.com").first():
        admin_user = User(
            username="admin",
            email="admin@emrsystem.com",
            password=generate_password_hash(
                "admin123"),  # Default password: admin123
            role="admin")
        db.session.add(admin_user)
        db.session.commit()
        print(
            "Admin account created: Email: admin@emrsystem.com, Password: admin123"
        )

# Shared CSS for Binance-like UI
css_styles = """
<style>
    body { font-family: Arial, sans-serif; background-color: #121212; color: #fff; text-align: center; margin-top: 50px; }
    .container { width: 350px; margin: auto; background: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px #000; }
    input, select, button { width: 90%; padding: 10px; margin: 10px; border: none; border-radius: 5px; }
    button { background-color: #f0b90b; color: #121212; font-weight: bold; cursor: pointer; }
    button:hover { background-color: #e5a300; }
    a { color: #f0b90b; text-decoration: none; }
    h2, h3 { margin-bottom: 20px; }
    .user-list { text-align: left; margin: 20px auto; width: 80%; }
    .user-list li { margin: 5px 0; }
</style>
"""

# Templates
register_template = css_styles + """
<div class="container">
    <h2>Register</h2>
    <form method="POST">
        <input type="text" name="username" placeholder="Username" required><br>
        <input type="email" name="email" placeholder="Email" required><br>
        <input type="password" name="password" placeholder="Password" required><br>
        <select name="role">
            <option value="doctor">Doctor</option>
            <option value="patient">Patient</option>
        </select><br>
        <button type="submit">Register</button>
    </form>
    <p>Already have an account? <a href="{{ url_for('login') }}">Login here</a></p>
</div>
"""

login_template = css_styles + """
<div class="container">
    <h2>Login</h2>
    <form method="POST">
        <input type="email" name="email" placeholder="Email" required><br>
        <input type="password" name="password" placeholder="Password" required><br>
        <button type="submit">Login</button>
    </form>
    <p>Don't have an account? <a href="{{ url_for('register') }}">Register here</a></p>
</div>
"""

admin_dashboard_template = css_styles + """
<div class="container">
    <h2>Admin Dashboard</h2>
    <h3>Set Doctor Access Expiry</h3>
    <form method="POST" action="{{ url_for('set_expiry') }}">
        <input type="text" name="doctor_email" placeholder="Doctor Email" required><br>
        <input type="date" name="expiry_date" required><br>
        <button type="submit">Set Expiry</button>
    </form>
    <h3>All Users</h3>
    <ul class="user-list">
    {% for user in users %}
        <li>{{ user.username }} ({{ user.role }}) {% if user.role == 'doctor' %} - Expires: {{ user.doctor_expiry }} {% endif %}</li>
    {% endfor %}
    </ul>
    <a href="{{ url_for('logout') }}">Logout</a>
</div>
"""

dashboard_template = css_styles + """
<div class="container">
    <h2>Welcome, {{ username }}!</h2>
    {% if role == 'doctor' or role == 'patient' %}
    <h3>Upload EMR</h3>
    <form method="POST" enctype="multipart/form-data" action="{{ url_for('upload_emr') }}">
        <input type="file" name="file" required><br>
        <button type="submit">Upload</button>
    </form>
    <h3>Retrieve EMR</h3>
    <form method="POST" action="{{ url_for('retrieve_emr') }}">
        <input type="text" name="filename" placeholder="Filename" required><br>
        <button type="submit">Retrieve</button>
    </form>
    {% endif %}
    <a href="{{ url_for('logout') }}">Logout</a>
</div>
"""

# Routes


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']

        if User.query.filter_by(email=email).first():
            flash('Email already exists!')
            return redirect(url_for('register'))

        user = User(username=username,
                    email=email,
                    password=password,
                    role=role)
        db.session.add(user)
        db.session.commit()
        flash('Registered successfully!')
        return redirect(url_for('login'))
    return render_template_string(register_template)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        flash('Invalid credentials!')
    return render_template_string(login_template)


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.role == 'admin':
        users = User.query.all()
        return render_template_string(admin_dashboard_template, users=users)
    return render_template_string(dashboard_template,
                                  username=user.username,
                                  role=user.role)


@app.route('/set_expiry', methods=['POST'])
def set_expiry():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    doctor_email = request.form['doctor_email']
    expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d')
    doctor = User.query.filter_by(email=doctor_email, role='doctor').first()
    if doctor:
        doctor.doctor_expiry = expiry_date
        db.session.commit()
        flash('Doctor access expiry updated.')
    else:
        flash('Doctor not found.')
    return redirect(url_for('dashboard'))


@app.route('/upload_emr', methods=['POST'])
def upload_emr():
    file = request.files['file']
    file.save(os.path.join("uploads", file.filename))
    flash('File uploaded successfully.')
    return redirect(url_for('dashboard'))


@app.route('/retrieve_emr', methods=['POST'])
def retrieve_emr():
    filename = request.form['filename']
    file_path = os.path.join("uploads", filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    flash('File not found.')
    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)
