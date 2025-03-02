# **Automated Question Answer Builder Application**  

![GitHub repo size](https://img.shields.io/github/repo-size/Faraazman/Automated-Question-Builder)  
![GitHub last commit](https://img.shields.io/github/last-commit/Faraazman/Automated-Question-Builder)  


## **📌 Overview**  
The **Automated Question Answer Builder** is an AI-powered application that generates curriculum-based and general-purpose questions from user-provided text prompts. Built using OpenAI’s 4.0 Turbo, this tool helps educators, students, and content creators streamline question creation.  

---

## **🚀 Features**  
✔ **Customizable Input** – Generate questions tailored to specific subjects or topics.  
✔ **Time-saving Automation** – Eliminates the need for manual question formulation.  
✔ **Versatile Use Cases** – Useful for education, training, and corporate learning.  
✔ **Scalable** – Can be extended for different industries and educational domains.  
✔ **Supports Learning & Knowledge Sharing** – Enhances assessment creation and knowledge transfer.  

---

## **🔧 Tech Stack**  
- **OpenAI GPT-3.5 Turbo** – AI model for question generation  
- **Python** – Backend implementation  
- **dotenv** – Environment variable management  
- **VS Code & GitHub** – Development and version control  

---

## **🛠 Installation & Setup**  

### **1️⃣ Clone the Repository**  
```sh
git clone https://github.com/Faraazman/Automated-Question-Builder.git
cd Automated-Question-Builder

2️⃣ Create a Virtual Environment (Optional but Recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Set Up OpenAI API Key
Create a .env file in the root directory.
Add the following line and replace your_api_key_here with your actual OpenAI API key:
OPENAI_API_KEY=your_api_key_here


5️⃣ Run the Application
python main.py
