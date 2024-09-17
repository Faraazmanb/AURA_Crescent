import random
import sys
import tempfile
from flask import Flask, Response, jsonify, render_template, redirect, send_from_directory, session, url_for, request, flash, send_file
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from pypdf import PdfReader
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from functools import wraps

import os

from mcq import generate_mcq_question
from ciriculam_based_QA import ciriculam_based_QA, generate_pdf


## Dashbaord
from admin_dashboard import *
import dash_bootstrap_components as dbc
from dash import dcc, html
from user_dashboard import *


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


mcq_a = ""


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
    
# Function to extract text from the PDF
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


# Serve the cir_question_gen.html file from the templates folder
@app.route('/question_form')
def serve_question_form():
    return render_template('cir_question_gen.html')

@app.route('/question_generator_pdf', methods=['POST'])
def question_generator_pdf():
    file = request.files['pdf']
    subject = request.form['subject']
    num_questions = int(request.form['num_questions'])
    difficulty = int(request.form['difficulty'])

    # Save uploaded PDF
    pdf_path = os.path.join(tempfile.gettempdir(), file.filename)
    file.save(pdf_path)

    # Generate questions using the updated ciriculam_based_QA function
    questions = ciriculam_based_QA(pdf_path, subject, num_questions, difficulty)

    # Generate a new PDF with the questions
    generated_pdf_path = generate_pdf(questions)

    # Read the generated PDF file to be served in the response
    with open(generated_pdf_path, 'rb') as pdf_file:
        pdf_data = pdf_file.read()

    # Serve the PDF inline by setting appropriate headers
    return Response(pdf_data, mimetype='application/pdf',
                    headers={"Content-Disposition": "inline; filename=generated_questions.pdf"})



## Dashboard starts from here

admin_dashboard = dash.Dash(
    __name__,
    server=app,
    url_base_pathname='/admin_dashboard/',
    external_stylesheets=[dbc.themes.SLATE]
)

admin_dashboard.layout = html.Div([
    dbc.Card(
        dbc.CardBody([

            
            dbc.Row([
                dbc.Col(drawText_Admin_Dashbaord(), width=20),
            ], align='center'),


            html.Br(),


            dbc.Row([
                dbc.Col(drawFigure_Users_Month(), width=3.5),
            ], align='center'),


            html.Br(),
            

            dbc.Row([
                dbc.Col(drawFigure_Users_Year(), width=4),
                dbc.Col(drawFigure_Users_Active(), width=3),
                dbc.Col(drawFigure_Users_Study_Time(), width=5),
                
            ]),

            html.Br(),

            dbc.Row([
                dbc.Col(drawFigure_Users_New_Users(), width=5),
                dbc.Col(drawFigure_Users_Name(), width=4),
                dbc.Col(drawFigure_Up_Time(), width=3),
            ],align='center'),


            html.Br(),


            dbc.Row([
                dbc.Col(drawFigure_Network_load(), width=9),
            ], align='center'),
        ]), color='dark'
    )
])


user_dashboard = dash.Dash(
    __name__,
    server=app,
    url_base_pathname='/user_dashboard/',
    external_stylesheets=[dbc.themes.SLATE]
)

user_dashboard.layout = html.Div([
    dbc.Card(
        dbc.CardBody([

            dbc.Row([
                dbc.Col(drawText_User_Dashbaord(), width=20),
            ], align='center'),


            html.Br(),
            
            dbc.Row([
                dbc.Col(drawFigure_Users_Month(), width=5),
            ], align='center'),

        ]), color='dark'
    )
])

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=5000)