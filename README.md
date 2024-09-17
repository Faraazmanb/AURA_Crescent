# AI-Based Question Generator Using GPT-3.5

## Project Overview

This project leverages OpenAI’s GPT-3.5 model to generate curriculum-based questions and general-purpose questions. The system is capable of taking a prompt, processing it via the OpenAI API, and returning questions or other relevant outputs.

### Features:
- **GPT-3.5 Turbo Integration**: Uses OpenAI's GPT-3.5 Turbo model to generate responses based on the input prompt.
- **Customizable Prompts**: Users can input any text, and the model will generate relevant questions based on the context provided.
- **Flexible Use Case**: Designed for generating questions for educational purposes, this system can be tailored to various domains or tasks by modifying the input prompt.

---

## Technologies Used

- **OpenAI GPT-3.5 Turbo**: Used for generating questions and other content from provided prompts.
- **Python**: The core language used to interact with the OpenAI API.
- **dotenv**: Used for managing environment variables, specifically the OpenAI API key.

---

## Getting Started

### Prerequisites

To run this project, you will need:

- **Python 3.x**
- **OpenAI API Key**
- The following Python libraries:
  ```bash
  pip install openai python-dotenv
  ```

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-repository.git
   cd your-repository
   ```

2. **Set up a virtual environment (optional but recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # For Linux/Mac
   venv\Scripts\activate     # For Windows
   ```

3. **Install required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   Create a `.env` file in the root directory of your project and add your OpenAI API key:
   ```
   OPENAI=your-openai-api-key
   ```

5. **Run the script:**

   ```bash
   python your_script.py
   ```

---

## Application Structure

### Core Functions

- **`chat_with_gpt(prompt)`**: 
  This function sends a user prompt to OpenAI's GPT-3.5 Turbo and returns the model's response. It's a simple interaction function, useful for getting quick answers from the GPT model.
  ```python
  def chat_with_gpt(prompt):
      chat_completion = client.chat.completions.create(
          messages=[{"role": "user", "content": prompt}],
          model="gpt-3.5-turbo",
      )
      return chat_completion.choices[0].message.content.strip()
  ```

- **`chatgpt_for_qa_cir(prompt)`**: 
  This function is more specific and structured for question generation. It uses a system message to define the role of the assistant (as a helpful assistant) and then processes the user’s prompt to generate a question. 
  ```python
  def chatgpt_for_qa_cir(prompt):
      response = client.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[
              {"role": "system", "content": "You are a helpful assistant."},
              {"role": "user", "content": prompt},
          ],
          max_tokens=150
      )
      return response.choices[0].message.content.strip()
  ```

### Example Usage:

1. **Generating Questions with GPT:**

   This example demonstrates how you can call the `chat_with_gpt` function to generate content from a prompt:

   ```python
   if __name__ == '__main__':
       prompt = "What are the effects of global warming?"
       response = chat_with_gpt(prompt)
       print(response)
   ```

2. **Curriculum-Based Question Generation:**

   Use the `chatgpt_for_qa_cir` function to generate more structured questions:

   ```python
   if __name__ == '__main__':
       prompt = "Generate a question about the theory of relativity."
       question = chatgpt_for_qa_cir(prompt)
       print(question)
   ```

---

## Environment Setup

To use the OpenAI API, you'll need to set up your API key as an environment variable. This ensures that your sensitive information is not hardcoded into the script.

1. **Creating a `.env` File:**

   Create a `.env` file in the root directory and add the following:
   ```
   OPENAI=your_openai_api_key
   ```

2. **Loading Environment Variables:**

   The API key is loaded into the application using `dotenv`:
   ```python
   from dotenv import load_dotenv
   import os

   load_dotenv()

   client = OpenAI(
       api_key=os.getenv('OPENAI'),
   )
   ```

---

## License

This project is licensed under the MIT License.

---

## Author

- Tiger

Feel free to reach out for any questions or contributions to this project.
