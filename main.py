from utils.api import V1

# Set your OpenAI API key
OPENAI_API_KEY = "your-api-key-here"

# Instantiate the V1 class
gpt = V1(key=OPENAI_API_KEY)

# Ask a question and print the response
prompt = "What is the meaning of life?"
response = gpt.ask(prompt)
print(response[0].answer)
