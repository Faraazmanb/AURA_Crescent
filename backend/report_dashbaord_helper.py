import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# 1. Questions Attempted Plot
def report_questions_attempt(data):
    # Bar plot for points over time
    fig = px.bar(
        data, 
        x='Time Taken (seconds)', 
        y='Points', 
        title='Questions Attempted and Points Over Time',
        labels={'x': 'Time Taken (seconds)', 'y': 'Points'}
    )
    return fig

# 2. Correct vs Incorrect Donut Chart
def report_correct_incorrect(data):
    # Count the number of occurrences for each status
    user_count_by_correct = data.groupby("Correct or Incorrect").size().reset_index(name='Count')

    # Define colors for each status
    colors = {
        "Correct": "green",
        "Incorrect": "orange",
    }

    # Create the donut chart
    fig = px.pie(
        user_count_by_correct,  
        names='Correct or Incorrect', 
        values='Count',  
        title='Correct vs Incorrect Answers',
        color='Correct or Incorrect',
        color_discrete_map=colors,
        hole=0.6  
    )
    
    return fig

# 3. Average Score Indicator
def report_avg_score(data):
    total_points = data['Points'].sum()  # Sum of points (where 1 is incorrect)
    avg_points = total_points / len(data)  # Calculate average
    previous_avg = 0.5  # Example reference for last month's average score

    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=(1 - avg_points) * 100,  # Calculate percentage of correct answers
        title="Average Score",
        domain={'x': [0, 1], 'y': [0, 1]},
        delta={'reference': previous_avg * 100, 'relative': True, 'position': "bottom"}
    ))
    
    return fig

# 4. Leaderboard (Separate from the main data)
def report_leaderboard(mongo_client):
    # leader = pd.DataFrame([
    #     ["Rahoul", 560],
    #     ["Ronak", 234],
    #     ["Joe", 154],
    #     ["Tony", 123],
    #     ["Shane", 112],
    #     ["Gillis", 83],
    #     ["Kam", 83],
    #     ["Patterson", 81],
    # ], columns=["Name", "Points"])

    db = mongo_client.db.user_scores
    data = db.find({}, {'_id': 0, 'username': 1, 'score': 1})
    leader_data = [(entry['username'], entry['score']) for entry in data]
    leader = pd.DataFrame(leader_data, columns=["Name", "Points"])
    leader.sort_values(by="Points", ascending=True).reset_index(drop=True)
    
    fig = px.bar(leader, x='Name', y='Points', title="Leaderboard")
    
    return fig

def time_taken_bar(data):
    fig = px.bar(
        data, 
        x=data.index + 1,  # Question number as x-axis
        y='Time Taken (seconds)', 
        title='Time Taken per Question',
        labels={'x': 'Question Number', 'y': 'Time Taken (seconds)'}
    )
    
    return fig
