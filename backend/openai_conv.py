from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

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
        model="gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message.content.strip()

def chatgpt_for_qa_cir(prompt):
    response = client_openrouter.chat.completions.create(
        model="gpt-3.5-turbo",
         messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
        max_tokens=150
    )
    return response.choices[0].message.content.strip()