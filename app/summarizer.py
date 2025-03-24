import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_text(text, max_tokens=300):
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant that summarizes news articles in a professional tone."},
            {"role": "user", "content": f"Summarize this news article:\n\n{text}"}
        ]

        response = openai.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo" if needed
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.6
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"[ERROR] GPT summarization failed: {e}")
        return None
