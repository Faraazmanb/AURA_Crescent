from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key= os.getenv('OPENAI'),
    )

client_openrouter = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv('OPENAI_OPENROUTER')
)

def chat_with_gpt(prompt):
    chat_completion = client_openrouter.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="openai/gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message.content.strip()

def chatgpt_for_qa_cir(prompt):
    response = client_openrouter.chat.completions.create(
        model="openai/gpt-3.5-turbo",
         messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
        max_tokens=150
    )
    return response.choices[0].message.content.strip()


def generate_mcq_question(topic, difficulty, asked, *_):
    """Generates mcq"""
    return chat_with_gpt(f"""generate an MCQ on the topic: {topic}; Difficulty - {difficulty}; where 0-20 is easy, 20-40 is medium, 40-60 is hard, 60-80 is difficult, 80-100 is extremly difficult; give 4 options, label options a,b,c,d; the last line must contain the correct option only [eg: a]
                    example:
                    
What is the unit of force in the International System of Units?
a.Newton
b.Joule
c.Watt
d.Amps
                         
a.Newton
                   
dont ask:
{asked}
                    """)

def generate_mcq_options(question, *_):
    """Generates mcq"""
    return chat_with_gpt(f"""generate an MCQ on the given question: {question}, give 4 options, label options a,b,c,d; the last line must contain the correct option only [eg: a.Newton]
                    example:
                    
What is the unit of force in the International System of Units?
a.Newton
b.Joule
c.Watt
d.Amps
                         
a.Newton""")

if __name__ == '__main__':
    mcq_qa = generate_mcq_question("hitorical figures", 100, "").splitlines()
    mcq_q = mcq_qa[0]
    mcq_options = mcq_qa[1:-1]
    mcq_a = ''.join(mcq_qa[-1])

    print(mcq_q)
    print(mcq_options)
    print(mcq_a)