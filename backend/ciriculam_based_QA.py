import tempfile
import openai
import pandas as pd
import PyPDF2
import random
from nltk.tokenize import sent_tokenize
from fpdf import FPDF
import nltk
import os
from openai_conv import chatgpt_for_qa_cir
from dotenv import load_dotenv

import ssl
import certifi

ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())

from pymongo import MongoClient

# Connect to MongoDB
db = client['users'] 
collection = db['trainer_question']

load_dotenv()

import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')


class AIQuestionGenerator:
    def __init__(self, filepath, output=None):
        self.output = output
        self.filepath = filepath
        # self.api_key = api_key
        # openai.api_key = self.api_key
        self.text = self._read_file()
        self.unwanted_phrases = []

    def add_unwanted_phrase(self, phrase):
        """Method to add a phrase to the unwanted_phrases array."""
        self.unwanted_phrases.append(phrase.lower())

    def _read_file(self):
        if self.filepath.endswith('.csv'):
            return self._read_csv()
        elif self.filepath.endswith('.pdf'):
            return self._read_pdf()
        else:
            raise ValueError("Unsupported file format. Use CSV or PDF files.")

    def _read_csv(self):
        df = pd.read_csv(self.filepath)
        text = ' '.join(df.astype(str).values.flatten())
        return text

    def _read_pdf(self):
        text = ""
        with open(self.filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        return text

    def analyze_text(self):
        sentences = sent_tokenize(self.text)
        return sentences

    def generate_questions(self, num_questions, difficulty, subject):
        prompts = []
        for sentence in self.analyze_text():
            prompt = self._generate_prompt(sentence, difficulty, subject)
            prompts.append(prompt)

        responses = []
        for idx, prompt in enumerate(prompts, start=1):

            question = str(idx) + ". " + chatgpt_for_qa_cir(prompt=prompt)
            responses.append(question)

            if len(responses) >= num_questions:
                break

        return responses

    def _generate_prompt(self, sentence, difficulty, subject):
        if difficulty == 'easy':
            base_prompt = (
                f"Generate one question based on the following {subject} domain and text that focus on broad concepts or practical applications. "
                "Avoid specific references to textbooks, authors, or publication details. The questions should be suitable "
                "for an exam setting and should test the understanding of key concepts or practical skills without delving into "
                "specific details or lists. "
            )
        elif difficulty == 'medium':
            base_prompt = (
                f"Generate one question that require a moderate understanding of {subject} domain and the underlying concepts presented in the following text. "
                "Focus on core ideas and their implications, making sure to test the understanding of nuanced aspects and practical applications. "
            )
        elif difficulty == 'hard':
            base_prompt = (
                f"Generate one challenging question that require deep comprehension of {subject} and the core concepts in the following text. "
                "These questions should push the learner to critically analyze the material, drawing connections between complex ideas and their applications. "
            )
        else:
            raise ValueError("Invalid difficulty level. Choose 'easy', 'medium', or 'hard'.")

        if 'formula' in sentence.lower() or 'equation' in sentence.lower() or 'specific concept' in sentence.lower():
            base_prompt = (
                "Generate one question about general understanding and applications of the following concept, ensuring the question "
                "is not directly derived from the provided content but focuses on practical or theoretical understanding. "
            )

        full_prompt = f"{base_prompt}: '{sentence}'"
        return full_prompt

    def is_too_specific(self, question):
        specific_terms = ['course objectives', 'syllabus', 'technical terms']
        return any(term in question.lower() for term in specific_terms)

    def contains_unwanted_phrase(self, question):
        return any(phrase in question.lower() for phrase in self.unwanted_phrases)

    def save_questions(self, questions, output_format='pdf'):
        # filename = input("Enter the filename (without extension): ")
        filename = self.output

        if output_format == 'pdf':
            self._save_as_pdf(questions, filename)
        elif output_format == 'excel':
            self._save_as_excel(questions, filename)
        else:
            raise ValueError("Unsupported output format. Choose 'pdf' or 'excel'.")

    def _save_as_pdf(self, questions, filename):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font('Arial', size=12)
        for question in questions:
            pdf.multi_cell(0, 10, question)
            pdf.ln()
        pdf.output(f"{filename}.pdf")

    def _save_as_excel(self, questions, filename):
        df = pd.DataFrame(questions, columns=["Questions"])
        df.to_excel(f"{filename}.xlsx", index=False)


def ciriculam_based_QA(filepath, subject, ques_number, difficulty):
    num_questions = ques_number
    hardness = 'medium'
    if int(difficulty) <= 33:
        hardness = 'easy'
    elif int(difficulty) >= 33:
        hardness = 'hard'
    difficulty = hardness
    ok = "y"
    generator = AIQuestionGenerator(filepath, None)
    generator.add_unwanted_phrase("key topics covered")
    generator.add_unwanted_phrase("common pitfalls")
    generator.add_unwanted_phrase("key considerations")
    questions = generator.generate_questions(num_questions, difficulty, subject)
    
    return questions
    # generator.save_questions(questions, pdforexcel)

def save_question(text):

    filter_query = {"id": "standard_id"}
    delete_result = collection.delete_one(filter_query)

    # Create a document
    question_document = {
        "id": "standard_id",
        "question": text
    }
    
    # Insert the document into the collection
    collection.insert_one(question_document)
    
    return {"id": "standard_id", "question": text}

all_questions = []
def generate_pdf(questions):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    for question in questions:
        all_questions.append(question)
        pdf.multi_cell(200, 10, question)
        pdf.ln()

    # Save to a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(temp_file.name)
    print("\n".join(all_questions))
    save_question("\n".join(all_questions))
    return temp_file.name


    