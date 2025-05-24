import openai
import os
from dotenv import load_dotenv

# Load the API key from the .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.5,
        max_tokens=500
    )
    return response.choices[0].message["content"]

# Ask a question about Module 10
user_input = input("Ask a Module 10 question: ")
reply = get_completion(user_input)
print("Assistant:", reply)

