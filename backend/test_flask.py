from flask import Flask, render_template, request, jsonify
from mcq import generate_mcq_options
import time
import uuid

app = Flask(__name__)

sample_doc = """1. How does the incorporation of Flynn's Taxonomy in the design of High-Performance Computing (HPC) Clusters impact the scalability and efficiency of parallel processing in distributed systems? Provide adetailed analysis of how key properties of HPC architectures such as vectorization, pipelining, and theMaster-Slave architecture contribute to achieving high performance in distributed computingenvironments.
2. How can the concept of parallelism be effectively utilized within computer clusters to achieve high performance computing, and what are the key challenges that need to be addressed when designing and optimizing parallel algorithms for such HPC clusters?"""

score = 0
all_questions = sample_doc.splitlines()
num_questions = len(all_questions)
number_asked_ques = 0
current_question = None
points = []
time_taken = []
start_time = None
unique_id = str(uuid.uuid4())

@app.route('/test')
def index():
    return render_template('test.html')

def generate_question():
    global number_asked_ques, current_question, start_time
    if number_asked_ques >= num_questions:
        return None
    mcq_qa = generate_mcq_options(all_questions[number_asked_ques]).splitlines()
    mcq_qa = [i for i in mcq_qa if i.strip() != '']
    mcq_q = all_questions[number_asked_ques]
    mcq_options = mcq_qa[:-1]
    mcq_options = [i for i in mcq_options if i.strip() != '']
    mcq_a = mcq_qa[-1].strip()  # Remove any whitespace
    current_question = {
        "question": mcq_q,
        "options": mcq_options,
        "answer": mcq_a,
    }
    number_asked_ques += 1
    start_time = time.time()
    return current_question

@app.route('/get_question', methods=['GET'])
def serve_question():
    global current_question
    if current_question is None:
        current_question = generate_question()
    if current_question is None:
        return jsonify({"redirect": "/report"})
    return jsonify({
        "question": current_question["question"],
        "options": current_question["options"][1:],
        "score": score
    })

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    global score, current_question, points, time_taken, start_time
    data = request.json
    user_answer = data.get('answer')
    correct_answer = current_question["answer"]
    is_correct = user_answer.lower()[0] == correct_answer.lower()[0]
    if is_correct:
        score += 1
        points.append(1)
    else:
        points.append(0)
    end_time = time.time()
    time_taken.append(round(end_time - start_time, 1))
    current_question = None  # Reset for next question
    return jsonify({
        "is_correct": is_correct,
        "correct_answer": correct_answer,
        "score": score
    })

@app.route('/report', methods=['GET'])
def report():
    global points, score, time_taken
    document = {
        "_id": "your_unique_id",
        "points": points,
        "score": score,
        "time_spent": time_taken
    }
    return jsonify(document)

if __name__ == '__main__':
    app.run(debug=True)