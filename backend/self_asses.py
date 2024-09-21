from analyzer import process_curriculum_file, analyze_curriculum, create_learning_plan

def request_plan(file_path, output):
    """Request personalised learning plan"""
    # file_path = input("Please enter the path to your curriculum file (.pdf or .docx): ")
    curriculum_text = process_curriculum_file(file_path)
    analysis_text = analyze_curriculum(curriculum_text)
    schedule_content = create_learning_plan(analysis_text, output)
    print("Learning plan document has been created as a PDF.")
    return schedule_content