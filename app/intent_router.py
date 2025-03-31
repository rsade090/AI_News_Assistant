import re
import difflib
from typing import List, Dict
from app.summarizer import summarize_text
from app.rag_qa import answer_question
from app.headline_generator import generate_headline

def match_article_by_title(user_query: str, articles, threshold=0.6):

    titles = [a["title"] for a in articles]
    match = difflib.get_close_matches(user_query, titles, n=1, cutoff=threshold)
    if match:
        return next((a for a in articles if a["title"] == match[0]), None)
    return None


def find_related_headlines(topic: str, vectorstore, k=5):

    results = vectorstore.similarity_search(topic, k=k)
    unique_titles = list({r.metadata['title']: r.metadata['url'] for r in results}.items())
    return unique_titles


def route_user_query(user_input: str, articles: List[Dict[str, str]], vectorstore, stream_function=None) -> str:

    user_input_lower = user_input.lower()

    return answer_question(user_input, vectorstore, articles, stream_function=stream_function)


def format_all_headlines(articles):
    """
    Format all article headlines as a list with links.
    """
    return "\n".join([f"- [{a['title']}]({a['url']})" for a in articles])


def extract_topic(text: str) -> str:
    """
    Extract the topic from the user's input.
    """
    words = re.findall(r'\b\w+\b', text.lower())
    stopwords = {"what", "is", "the", "are", "related", "articles", "about", "show", "me", "please"}
    keywords = [w for w in words if w not in stopwords]
    return " ".join(keywords)