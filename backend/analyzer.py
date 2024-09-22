import os
from openai import OpenAI
import docx
import PyPDF2
from docCreator import create_learning_plan
from dotenv import load_dotenv
load_dotenv()


def read_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    
client_openrouter = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv('OPENAI_OPENROUTER')
)

def analyze_curriculum(curriculum_text, use_turbo=False):
    model = "gpt-3.5-turbo"

    prompt = f"""Analyze the following curriculum and create a study plan:\n\n{curriculum_text}

example:
Study Plan for B.Tech. Information Technology - Materials Science for Engineering

Week 1-2:
Module I - Intro to Course
Introduction to the course and its objectives. Understanding the basics of materials science and engineering. 

Week 3-4: 
Module II - Classification of Materials
Focus on the concept of amorphous, single crystals, and polycrystalline materials. Understand the effects of crystallinity on physical properties.

add how many weeks needed.
format:
Week (no new lines)
Module (no new lines)
Description (no new lines)

MAKE SURE THAT:
Week has a start and end
Week 1: (NOT ALLOWED)
Week 0-1 (ALLOWED)
"""
    
    response = client_openrouter.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an educational planner."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def process_curriculum_file(file_path):
    # Determine file type and extract text
    if file_path.endswith('.docx'):
        return read_docx(file_path)
    elif file_path.endswith('.pdf'):
        return read_pdf(file_path)
    else:
        raise ValueError("Unsupported file type. Please provide a .pdf or .docx file.")

if __name__ == "__main__":
    file_path = input("Please enter the path to your curriculum file (.pdf or .docx): ")
    curriculum_text = process_curriculum_file(file_path)
    analysis = analyze_curriculum(curriculum_text, use_turbo=False)  # Set use_turbo=False to use regular GPT-4
    create_learning_plan(analysis)
    print("Learning plan document has been created as a PDF.")
