import random
import sys
from flask import Flask, jsonify, render_template, redirect, session, url_for, request, flash
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from functools import wraps

from mcq import generate_mcq_question

import ssl
import certifi

ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())

app=Flask(__name__)


# Other cluster until hamdan gives access
app.config['SECRET_KEY']="hexawareSecretKey"
app.config['MONGO_URI']="mongodb+srv://arxiv:Dorem%40n101@arxiv.21plqx0.mongodb.net/users"


# app.config['MONGO_URI']="mongodb+srv://hamdanaveed07:hexaware@cluster0.gew2p.mongodb.net/users"


mongo=PyMongo(app, tlsCAFile=certifi.where())
try:
    mongo.db.command('ping')
    print("Connected to MongoDB successfully")
except Exception as e:
    raise SystemExit(f"Error connecting to MongoDB: {e}")
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, username,role,password,user_id=None):
        self.username = username
        self.role=role
        self.password_hash=password
        self.id=user_id

    @staticmethod
    def find_by_username(username):
        user_data = mongo.db.users.find_one({"username": username})
        if user_data:
            return User(user_data['username'], user_data['role'], user_data['password'], str(user_data['_id']))
        return None
    @staticmethod
    def register_user(username, password, role):
        hashed_password = generate_password_hash(password)
        user_data = {"username": username, "password": hashed_password, "role": role}
        mongo.db.users.insert_one(user_data)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

    @login_manager.user_loader
    def load_user(user_id):

        user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:

            return User(user_data['username'], user_data['role'], user_data['password'], str(user_data['_id']))
        return None
# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_data['username'], user_data['role'], user_data['password'], str(user_data['_id']))
    return None

# Custom decorator for role-based access
def role_required(role):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role != role:
                flash(f'Access restricted to {role} role')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return wrapped
    return wrapper

# Home or dashboard route for all users
@app.route('/dashboard')
@login_required
def dashboard():
    return f"Hello, {current_user.username}! You are logged in as a {current_user.role}"

# Admin dashboard (restricted to 'Administrator')
@app.route('/admin')
@login_required
@role_required('Administrator')
def admin_dashboard():
    return "Welcome to the Admin Dashboard"

# Trainer dashboard (restricted to 'Trainer')
@app.route('/trainer')
@login_required
@role_required('Trainer')
def trainer_dashboard():
    return "Welcome to the Trainer Dashboard"

# Employee dashboard (restricted to 'Employee')
@app.route('/employee')
@login_required
@role_required('Employee')
def employee_dashboard():
    return "Welcome to the Employee Dashboard"

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')  # 'Administrator', 'Trainer', or 'Employee'

        # Check if user already exists
        if User.find_by_username(username):
            flash('Username already exists')
            return redirect(url_for('register'))
        
        # Register new user
        User.register_user(username, password, role)
        flash('User registered successfully')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.find_by_username(username)
        
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password','error')
            return redirect(url_for('login'))

    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Default route for starting the app
@app.route('/')
def home():
    return redirect(url_for('login'))

###


questions = [
    {
        "id": 1,
        "question": "What is the capital of France?",
        "options": ["London", "Berlin", "Paris", "Madrid"],
        "correct_answer": "Paris"
    },
    {
        "id": 2,
        "question": "Which planet is known as the Red Planet?",
        "options": ["Venus", "Mars", "Jupiter", "Saturn"],
        "correct_answer": "Mars"
    },
    {
        "id": 3,
        "question": "What is the largest mammal in the world?",
        "options": ["African Elephant", "Blue Whale", "Giraffe", "Hippopotamus"],
        "correct_answer": "Blue Whale"
    }
]

# mcq_qa = generate_mcq_question("hitorical figures", 100, "").splitlines()
# mcq_q = mcq_qa[0]
# mcq_options = mcq_qa[1:-1]
# mcq_a = ''.join(mcq_qa[-1])

mcq_a = ""

def generate_mcq_question2(topic, token_length, style):
    # This is a placeholder function. Replace it with your actual question generation logic.
    questions = [
        "Who was the first President of the United States?\nA) George Washington\nB) Thomas Jefferson\nC) John Adams\nD) Benjamin Franklin\nA",
        "Who painted the Mona Lisa?\nA) Vincent van Gogh\nB) Leonardo da Vinci\nC) Pablo Picasso\nD) Michelangelo\nB",
        "Who wrote 'Romeo and Juliet'?\nA) Charles Dickens\nB) Jane Austen\nC) William Shakespeare\nD) Mark Twain\nC"
    ]
    return random.choice(questions)

@app.route('/questions')
def quiz_questions():
    session['score'] = 0
    return render_template('questions.html')

asked = []

@app.route('/get_question')
def get_question():
    global mcq_a
    mcq_qa = generate_mcq_question("historical figures", 100, "\n".join(asked)).splitlines()
    mcq_q = mcq_qa[0]
    asked.append(mcq_q)
    mcq_options = mcq_qa[1:-1]
    mcq_a = mcq_qa[-1].strip()  # Remove any whitespace

    print(mcq_q)
    print(mcq_options)
    print(mcq_a)
    
    return jsonify({
        "question": mcq_q,
        "options": mcq_options,
        "score": session.get('score', 0)  # Include the current score in the response
    })

@app.route('/check_answer', methods=['POST'])
def check_answer():
    global mcq_a
    data = request.json
    user_answer = data.get('answer')
    
    if user_answer:
        print(user_answer)
        print(mcq_a)
        is_correct = user_answer == mcq_a[0]
        if is_correct:
            session['score'] = session.get('score', 0) + 1
        return jsonify({
            "correct": is_correct,
            "correct_answer": mcq_a,
            "score": session.get('score', 0)  # Include the updated score in the response
        })
    else:
        return jsonify({"error": "Invalid answer"}), 400

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)