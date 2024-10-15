from openai import OpenAI
import os
from dotenv import load_dotenv

from azure.cognitiveservices.search.imagesearch import ImageSearchClient
from msrest.authentication import CognitiveServicesCredentials

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

client_bing = ImageSearchClient(endpoint='https://api.bing.microsoft.com/', credentials=CognitiveServicesCredentials(os.getenv('BING')))
client_bing.config.base_url = '{Endpoint}/v7.0'

def get_image_url(client, query: str):    
    image_results = client.images.search(query=query)
    return image_results.value[0].content_url

def generate_mcq_question_image(topic, difficulty, asked, *_):
    """Generates mcq"""
    chat_reply =  chat_with_gpt(f"""generate an MCQ options about the image on the topic: {topic}; Difficulty - {difficulty}; where 0-20 is easy, 20-40 is medium, 40-60 is hard, 60-80 is difficult, 80-100 is extremly difficult; give 4 options, label options a,b,c,d; the last line must contain the correct option only [eg: a]
                         user will be given an image of the question
                    example:
                    
Indentify this person:
a.Newton
b.Joule
c.Watt
d.Amps 
                                           
a.Newton
                   
dont ask:
{asked}
                    """)
    to_format = chat_reply.split('\n')
    return to_format[0] + '\n' + get_image_url(client_bing, to_format[-1][3:]) + '\n' + "\n".join(to_format[1:-2]) + '\n' + to_format[-1]