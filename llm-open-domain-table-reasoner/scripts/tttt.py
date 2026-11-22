import openai
import os

# Set the API key explicitly (use the terminal's value if needed)
openai.api_key = os.getenv("OPENAI_API_KEY", "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")

# Test API call using ChatCompletion
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "system", "content": "You are a helpful assistant."},
              {"role": "user", "content": "What's the weather like today?"}]
)

# Print the response
print(response['choices'][0]['message']['content'])
