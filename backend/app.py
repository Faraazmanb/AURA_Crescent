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
from flask_mail import Mail, Message
import json

from time import time
import os

from mcq import generate_mcq_options, generate_mcq_question
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

from make_grant_for_time_table import *
from werkzeug.utils import secure_filename
from self_asses import request_plan
import io
import plotly

app=Flask(__name__)

# Other cluster until hamdan gives access
app.config['SECRET_KEY']=str(random.random())
app.config['MONGO_URI']="mongodb+srv://hamdanaveed07:hexaware@cluster0.gew2p.mongodb.net/users"


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '4tpurpose101@gmail.com'
app.config['MAIL_PASSWORD'] = 'ocgm npgr urtl sbaf'
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

mail = Mail(app)


# app.config['MONGO_URI']="mongodb+srv://hamdanaveed07:hexaware@cluster0.gew2p.mongodb.net/users"


mongo=PyMongo(app, tlsCAFile=certifi.where())
try:
    mongo.db.command('ping')
    print("Connected to MongoDB successfully")
except Exception as e:
    raise SystemExit(f"Error connecting to MongoDB: {e}")
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/'


class User(UserMixin):
    def __init__(self, username,role,email=None,user_id=None):
        self.username = username
        self.role=role
        self.email=email
        self.id=user_id

    @staticmethod
    def find_by_username(username):
        user_data = mongo.db.users.find_one({"username": username})
        if user_data:
            return User(user_data['username'], user_data['role'], user_data['email'], str(user_data['_id']))
        return None
    @staticmethod
    def register_user(username,email, password, role):
        hashed_password = generate_password_hash(password)
        user_data = {"username": username, "email":email, "password": hashed_password, "role": role}
        mongo.db.users.insert_one(user_data)

    def check_password(self, password):
        # This method can now access the stored hashed password directly from the database
        user_data = mongo.db.users.find_one({"username": self.username})
        if user_data:
            return check_password_hash(user_data['password'], password)
        return False
    

    @login_manager.user_loader
    def load_user(user_id):

        if user_id is None:
            return None
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
    return render_template('index2.html', username=current_user.username, role=current_user.role)
    




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

# # Registration route
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         role = request.form.get('role')  # 'Administrator', 'Trainer', or 'Employee'

#         # Check if user already exists
#         if User.find_by_username(username):
#             flash('Username already exists')
#             return redirect(url_for('register'))
        
#         # Register new user
#         User.register_user(username, password, role)
#         flash('User registered successfully')
#         return redirect(url_for('login'))

#     return render_template('register.html')

# # Login route
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         user = User.find_by_username(username)
        
#         if user and user.check_password(password):
#             login_user(user)
#             flash('Logged in successfully!', 'success')
#             return redirect(url_for('dashboard'))
#         else:
#             flash('Invalid username or password','error')
#             return redirect(url_for('login'))

#     return render_template('login.html')

# Logout route
@app.route('/logout',methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))




@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Determine which form was submitted based on the presence of 'email'
        if 'email' in request.form:
            # Registration form was submitted
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role')  # 'Administrator', 'Trainer', or 'Employee'
            if not username or not email or not password or not role:
                flash('Please fill out all fields.', 'error')
                return redirect(url_for('home'))

            # Check if user already exists
            if User.find_by_username(username):
                flash('Username already exists', 'error')
                return redirect(url_for('home'))

            # Register new user
            User.register_user(username, email, password, role)
            flash('User registered successfully! You can now log in.', 'success')
            return redirect(url_for('home'))

        
        else:
            # Login form was submitted
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.find_by_username(username)
            
            if user and user.check_password(password):
                login_user(user)
                # flash('Logged in successfully!', 'success')
                return render_template('index.html', username=current_user.username, role=current_user.role)
                # return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
                return redirect(url_for('home'))

    # GET request renders the combined form
    return render_template('loginreg.html')





# Default route for starting the app
# @app.route('/')
# def home():
#     return redirect(url_for('login'))

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

mail = Mail(app)

@app.route('/send_pdf_emails', methods=['POST'])
def send_pdf_emails():
    # Get the list of recipient emails from the request
    emails = json.loads(request.form['emails'])
    
    # Get the PDF file from the request
    if 'pdf' not in request.files:
        return jsonify({'message': 'No PDF file in the request'}), 400
    pdf_file = request.files['pdf']
    
    # Send email to each recipient
    for email in emails:
        msg = Message("Generated Questions PDF",
                      sender="your_email@example.com",
                      recipients=[email])
        msg.body = "Please find attached the generated questions PDF."
        msg.attach("generated_questions.pdf", "application/pdf", pdf_file.read())
        mail.send(msg)
        pdf_file.seek(0)  # Reset file pointer for the next iteration
    
    return jsonify({'message': f'Emails sent successfully to {len(emails)} recipients'}), 200


@app.route('/get_employee_emails', methods=['GET'])
def get_employee_emails():
    # Query MongoDB for users with the role 'employee'
    employees = mongo.db.users.find({ 'role': 'Employee' }, { 'email': 1, '_id': 0 })
    
    # Extract emails from the result
    emails = [employee['email'] for employee in employees]
    
    # Return the list of emails as a JSON response
    print(emails)
    return {'employee_emails': emails}

### Dashbaord

# Create the first Dash app for the admin dashboard
admin_dashboard = dash.Dash(
    __name__,
    server=app,
    url_base_pathname='/Administrator_dashboard/',
    external_stylesheets=[dbc.themes.SLATE]
)


trainer_dashboard = dash.Dash(
    __name__,
    server=app,
    url_base_pathname='/Trainer_dashboard/',
    external_stylesheets=[dbc.themes.SLATE]
)
from flask import redirect, url_for



user_dashboard = dash.Dash(
    __name__,
    server=app,
    url_base_pathname='/Employee_dashboard/',
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



trainer_dashboard.layout = html.Div([
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



### Time Table 
@app.route('/time_table', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            return redirect(url_for('display_figure', filename=filename))
    return render_template('upload.html')
@app.route('/display/<filename>')
def display_figure(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    text = request_plan(file_path, current_time)
    
    if not text:
        return "Error: Unable to process the PDF file."
    
    start_idx = 0
    split = text.splitlines()
    for idx, i in enumerate(split):
        if i.lower().startswith("week"):
            start_idx = idx
            break

    text_split = text.splitlines()

    if len(text_split) > 2:
        text_split = text_split[start_idx:]
    else:
        return "Error: Insufficient data in the processed text."
    
    weeks_ranges = []
    module = []
    descriptions = []

    i = 0
    for i in range(0, len(text_split), 4):
        if i + 3 < len(text_split):  # Check if indices are within bounds
            weeks_ranges.append(text_split[i])
            module.append(text_split[i + 1])
            descriptions.append(text_split[i + 2])
        else:
            # Handle the case where there are not enough elements
            break  # or return an error message

    if not weeks_ranges or not module or not descriptions:
        return "Error: Unable to extract necessary information from the PDF."
    
    print(text)
    print("")
    print(weeks_ranges)
    print("")
    print(module)
    print("")
    print(descriptions)
    print("")
    print(start_idx)
    print(text_split)
    
    weeks_start, weeks_end = convert_week_ranges(weeks_ranges)
    print(weeks_start)
    print(weeks_end)
    
    # Create Plotly figure
    fig = create_plotly_figure(weeks_start, weeks_end, module, descriptions)
    
    # Convert the figure to JSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('figure.html', graphJSON=graphJSON)

def create_plotly_figure(weeks_start, weeks_end, module, descriptions):
    # Create a trace for each module
    data = []
    for i, (start, end, mod, desc) in enumerate(zip(weeks_start, weeks_end, module, descriptions)):
        trace = go.Bar(
            x=[start.strftime('%b %d, %Y'), end.strftime('%b %d, %Y')],
            y=[mod],
            text=[desc],
            name=mod,
            marker=dict(
                color=f'rgb({i*20}, {i*30}, {i*40})'
            )
        )
        data.append(trace)

    # Create the layout
    layout = go.Layout(
        title='Course Schedule',
        xaxis_title='Week',
        yaxis_title='Module',
        barmode='stack',
        bargap=0.1,
        xaxis_type='category'
    )

    # Create the figure
    fig = go.Figure(data=data, layout=layout)

    return fig


### Trainer Based MCQ


# sample_doc = """1. How does the incorporation of Flynn's Taxonomy in the design of High-Performance Computing (HPC) Clusters impact the scalability and efficiency of parallel processing in distributed systems? Provide a detailed analysis of how key properties of HPC architectures such as vectorization, pipelining, and the Master-Slave architecture contribute to achieving high performance in distributed computing environments.
# 2. How can the concept of parallelism be effectively utilized within computer clusters to achieve high performance computing, and what are the key challenges that need to be addressed when designing and optimizing parallel algorithms for such HPC clusters?
# 3.Tallest building in the world"""

filter_query = {"id": "standard_id"}
# doc = mongo.db.trainer_question.find_one(filter_query)['question']
# all_questions = doc.splitlines()
# num_questions = len(all_questions)

@app.route('/test')
def index():
    global num_questions, all_questions
    print("now")
    doc = mongo.db.trainer_question.find_one(filter_query)['question']
    all_questions = doc.splitlines()
    num_questions = len(all_questions)
    return render_template('test.html')


def admin_generate_question():
    # Get number of questions asked from session
    number_asked_ques = session.get('number_asked_ques', 0)

    if number_asked_ques >= num_questions:
        return None  # Quiz is complete
    
    mcq_qa = generate_mcq_options(all_questions[number_asked_ques]).splitlines()
    mcq_qa = [i for i in mcq_qa if i.strip() != '']
    mcq_q = all_questions[number_asked_ques]
    mcq_options = mcq_qa[1:5]
    mcq_options = [i for i in mcq_options if i.strip() != '']
    mcq_a = mcq_qa[-1].strip()

    current_question = {
        "question": mcq_q,
        "options": mcq_options,
        "answer": mcq_a,
    }

    # Increment the number of asked questions in session
    session['number_asked_ques'] = number_asked_ques + 1
    session['start_time'] = time()  # Store start time in session

    return current_question


@app.route('/admin_get_question', methods=['GET'])
def serve_question():
    # Retrieve or generate the current question
    current_question = session.get('current_question')

    if current_question is None:
        current_question = admin_generate_question()

    if current_question is None:
        print("lol")
        return jsonify({"redirect": "/report/"})
    
    session['current_question'] = current_question  # Store the current question in session

    return jsonify({
        "question": current_question["question"],
        "options": current_question["options"][:4],
        "score": session.get('admin_score', 0)
    })


@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    # Get session data
    current_question = session.get('current_question')
    if not current_question:
        return jsonify({"error": "No current question available"}), 400
    
    data = request.json
    user_answer = data.get('answer')
    if not user_answer:
        return jsonify({"error": "No answer provided"}), 400
    
    # Validate the answer
    correct_answer = current_question["answer"]
    is_correct = user_answer.lower().strip()[0] == correct_answer.lower().strip()[0]

    # Update the score in session
    admin_score = session.get('admin_score', 0)
    admin_points = session.get('admin_points', [])
    admin_time_taken = session.get('admin_time_taken', [])
    start_time = session.get('start_time', time())

    if is_correct:
        admin_score += 1
        admin_points.append(1)
    else:
        admin_points.append(0)

    end_time = time()
    admin_time_taken.append(round(end_time - start_time, 1))

    # Store updated data back in session
    session['admin_score'] = admin_score
    session['admin_points'] = admin_points
    session['admin_time_taken'] = admin_time_taken
    session['current_question'] = None  # Reset current question

    # Optionally update the score in the database or perform some other action
    update_or_insert_score(admin_score, admin_points, admin_time_taken)

    number_asked_ques = session.get('number_asked_ques', 0)
    if number_asked_ques >= num_questions:
        print("lol")
        return jsonify({"redirect": "/report/"})
    
    return jsonify({
        "is_correct": is_correct,
        "correct_answer": correct_answer,
        "score": admin_score
    })


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)