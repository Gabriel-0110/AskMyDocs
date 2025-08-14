import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def ask_claude(prompt):
    response = client.messages.create(
        model="claude-opus-4-1-20250805",  # Opus 4.1
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


if __name__ == "__main__":
    print(ask_claude("Hello from Claude Opus 4.1 API!"))
