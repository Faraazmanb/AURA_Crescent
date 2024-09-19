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

from time import time
import os

from mcq import generate_mcq_question
from ciriculam_based_QA import ciriculam_based_QA, generate_pdf

import ssl
import certifi

ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())

import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc
import dash
from dash.dependencies import Input, Output

from admin_dashboard import *
from user_dashboard import *
from report_dashboard import *


app=Flask(__name__)

# Other cluster until hamdan gives access
app.config['SECRET_KEY']=str(random.random())
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

all = []
mcq_a = ""


@app.route('/questions')
def quiz_questions():
    session['score'] = 0
    return render_template('questions.html')

asked_questions = []


@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    data = request.json
    subject = data.get('subject')
    hardness_level = data.get('hardness_level')
    num_questions = data.get('num_questions', 10)  # Default to 10 if not provided

    # Store values in session or other storage
    session['subject'] = subject
    session['hardness_level'] = hardness_level
    session['total_questions'] = num_questions
    session['asked'] = []
    session['score'] = 0


    return jsonify({"message": "Quiz started", "subject": subject, "hardness_level": hardness_level})

points = []
time_taken = []
all.append([points, time_taken])

p = []

@app.route('/get_question')
def get_question():
    subject = session.get('subject', "default_subject")
    hardness_level = session.get('hardness_level', 1)
    num_questions = session.get('total_questions', 10)
    asked = session.get('asked', [])

    if len(asked) >= num_questions:
        return jsonify({"redirect": "/report/"})  # Redirect to the report page if done

    global mcq_a
    mcq_qa = generate_mcq_question(subject, hardness_level, "\n".join(asked_questions)).splitlines()
    mcq_q = mcq_qa[0]
    asked.append(mcq_q)
    asked_questions.append(mcq_q)
    mcq_options = mcq_qa[1:-1]
    mcq_a = mcq_qa[-1].strip()  # Remove any whitespace

    session['asked'] = asked  # Update the asked questions list

    return jsonify({
        "question": mcq_q,
        "options": mcq_options,
        "score": session.get('score', 0)  # Include the current score in the response
    })


def update_or_insert_score(score, points, time_spent):
    # Define the filter to find the document
    filter_query = {"_id": "your_unique_id"}  # Replace with the appropriate unique identifier

    # Get the collection
    collection = mongo.db.scores  # Collection name

    # Step 1: Delete the existing document if it exists
    delete_result = collection.delete_one(filter_query)

    # Step 2: Insert a new document with the updated values
    new_data = {
        "_id": "your_unique_id",  # Replace with the same unique identifier
        "score": score,
        "points": points,
        "time_spent": time_spent
    }

    insert_result = collection.insert_one(new_data)

    # Return a message based on the result
    if insert_result.inserted_id:
        return f'Inserted new document with ID: {insert_result.inserted_id}'
    else:
        return 'Failed to insert new document'
    

def retrieve_data(unique_id="your_unique_id"):
    """
    Retrieve a document from the MongoDB collection based on the unique ID.
    If the document is not found, return a dummy data set.

    :param unique_id: The unique identifier for the document
    :return: A DataFrame containing the document data or dummy data if not found
    """
    # Get the collection
    collection = mongo.db.scores  # Collection name

    # Define the query
    query = {"_id": unique_id}  # Replace with your unique identifier field if different

    # Retrieve the document
    document = collection.find_one(query)

    # If the document is not found, create dummy data
    if document is None:
        document = {
            "_id": unique_id,
            "points": [0, 1, 1],  # Example data: 0 = Correct, 1 = Incorrect
            "score": 2,           # Example score
            "time_spent": [2, 3, 4]  # Example time spent on questions
        }

    # Create a DataFrame from the document data
    data = pd.DataFrame({
        'Time Taken (seconds)': document['time_spent'],
        'Points': document['points'],  # 0 = Correct, 1 = Incorrect
    })

    # Add a new column for correctness
    data['Correct or Incorrect'] = data['Points'].map({0: 'Correct', 1: 'Incorrect'})

    print(document)
    return data
    

@app.route('/check_answer', methods=['POST'])
def check_answer():
    # Ensure 'points' and 'time_taken' are in the session
    if 'points' not in session:
        session['points'] = []
    if 'time_taken' not in session:
        session['time_taken'] = []

    data = request.json
    start = time()
    user_answer = data.get('answer')
    end = time()

    if user_answer:
        # Calculate time taken for the question
        time_spent = end - start
        session['time_taken'].append(time_spent)
        
        # Debugging: Print session data
        print('Updated time_taken:', session['time_taken'])

        # Check if the answer is correct
        is_correct = user_answer == mcq_a[0]
        if is_correct:
            session['score'] = session.get('score', 0) + 1
            session['points'].append(1)
        else:
            session['points'].append(0)

        # Debugging: Print session data
        print('Updated points:', session['points'])

        # Save the session changes
        session.modified = True

        update_or_insert_score(session['score'], session['points'], session['time_taken'])

        return jsonify({
            "correct": is_correct,
            "correct_answer": mcq_a,
            "score": session.get('score', 0)  # Include the updated score in the response
        })
    else:
        return jsonify({"error": "Invalid answer"}), 400


# @app.route('/report')
# def report():
#     score = session.get('score', 0)
#     total_questions = session.get('total_questions', 0)
#     return render_template('report.html', score=score, total_questions=total_questions)
    
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

### Dashbaord

# Create the first Dash app for the admin dashboard
admin_dashboard = dash.Dash(
    __name__,
    server=app,
    url_base_pathname='/admin_dashboard/',
    external_stylesheets=[dbc.themes.SLATE]
)
from flask import redirect, url_for



user_dashboard = dash.Dash(
    __name__,
    server=app,
    url_base_pathname='/user_dashboard/',
    external_stylesheets=[dbc.themes.SLATE]
)

report_dashboard = dash.Dash(
    __name__,
    server=app,
    url_base_pathname='/report/',
    external_stylesheets=[dbc.themes.SLATE]
)

# Build App Layout
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




user_dashboard.layout = html.Div([
    dbc.Card(
        dbc.CardBody([

            dbc.Row([
                dbc.Col(drawText_User_Dashbaord(), width=20),
            ], align='center'),


            html.Br(),
            
            dbc.Row([
                dbc.Col(drawFigure_Test_Insight(), width=3),
                dbc.Col(drawFigure_Users_Month(), width=5),
                dbc.Col(drawFigure_Correct_Incorrect(), width=4),

            ], align='center'),

            html.Br(),

            dbc.Row([
                dbc.Col(drawFigure_Average(), width=3),
                dbc.Col(drawFigure_User_activity(), width=3),
                dbc.Col(drawFigure_Leaderbaord(), width=5),

            ], align='center'),

            html.Br(),

        ]), color='dark'
    )
])

data_quiz_from_endpoint = pd.DataFrame(columns=['Time Taken (seconds)', 'Points', 'Correct or Incorrect'])

# dummy = pd.DataFrame({
#         'Time Taken (seconds)': time_taken,
#         'Points': points,  # 0 = Correct, 1 = Incorrect
#     })
# dummy['Correct or Incorrect'] = dummy['Points'].map({0: 'Correct', 1: 'Incorrect'})


# Callback to run hello() function and update content
report_dashboard.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col(drawText_Report_Dashbaord(), width=20),
            ], align='center'),

            html.Br(),
            
            dbc.Row([
                dcc.Interval(id='interval-component', interval=10*1000, n_intervals=0),

                dbc.Col(dcc.Loading(id='loading-figure-1', children=[html.Div(id='figure-correct-incorrect')]), width=3),
                dbc.Col(dcc.Loading(id='loading-figure-2', children=[html.Div(id='figure-average-score')]), width=3),
                dbc.Col(dcc.Loading(id='loading-figure-3', children=[html.Div(id='figure-time-taken')]), width=3),
                dbc.Col(dcc.Loading(id='loading-figure-4', children=[html.Div(id='figure-leaderboard')]), width=3),
            ], align='center'),

            html.Br(),
        ]), color='dark'
    )
])

# Define callback to update figures
@report_dashboard.callback(
    Output('figure-correct-incorrect', 'children'),
    Output('figure-average-score', 'children'),
    Output('figure-time-taken', 'children'),
    Output('figure-leaderboard', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_figures(n_intervals):
    data = retrieve_data()  # Fetch the latest data
    return (
        drawFigure_Correct_incorrect(data),
        drawFigure_Average_score_Report(data),
        drawFigure_Time_Taken(data),
        drawFigure_Leaderbaord_Report()
    )
# Callback to update figures on interval
# @report_dashboard.callback(
#     [Output('correct-incorrect-fig', 'figure'),
#      Output('average-score-fig', 'figure'),
#      Output('time-taken-fig', 'figure'),
#      Output('leaderboard-fig', 'figure')],
#     [Input('interval-component', 'n_intervals')]  # Triggered by the interval component
# )
# def update_figures(n):
#     # Fetch fresh data
#     data = retrieve_data()

#     # Generate and return updated figures
#     return (
#         drawFigure_Correct_incorrect(data),
#         drawFigure_Average_score_Report(data),
#         drawFigure_Time_Taken(data),
#         drawFigure_Leaderbaord_Report()
#     )

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)