import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_headline(text, max_tokens=30):
    try:
        messages = [
            {"role": "system", "content": "You are a journalist trained in writing concise, SEO-optimized headlines for news articles."},
            {"role": "user", "content": f"Generate an SEO-friendly headline for the following article:\n\n{text}"}
        ]

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[ERROR] GPT headline generation failed: {e}")
        return None
