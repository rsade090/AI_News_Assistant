import re
import difflib
from typing import List, Dict
from app.summarizer import summarize_text
from app.rag_qa import answer_question
from app.headline_generator import generate_headline

def match_article_by_title(user_query: str, articles, threshold=0.6):
    """
    Match the user's query to an article title using fuzzy matching.
    """
    titles = [a["title"] for a in articles]
    match = difflib.get_close_matches(user_query, titles, n=1, cutoff=threshold)
    if match:
        return next((a for a in articles if a["title"] == match[0]), None)
    return None


def find_related_headlines(topic: str, vectorstore, k=5):
    """
    Find related headlines using the vectorstore's similarity search.
    """
    results = vectorstore.similarity_search(topic, k=k)
    unique_titles = list({r.metadata['title']: r.metadata['url'] for r in results}.items())
    return unique_titles


def route_user_query(user_input: str, articles: List[Dict[str, str]], vectorstore) -> str:
    """
    Route the user's query to the appropriate handler based on intent.
    """
    user_input_lower = user_input.lower()

    # Case 1: Show all headlines
    if "headlines" in user_input_lower or "latest news" in user_input_lower:
        return format_all_headlines(articles)

    # Case 2: Summarize a known article
    if "summarize" in user_input_lower:
        article = match_article_by_title(user_input, articles)
        if article:
            return f"📄 **Summary:**\n{summarize_text(article['text'])}"
        else:
            return "❌ Sorry, couldn't find an article matching that title."

    # Case 3: Show full article
    if "full article" in user_input_lower or "more about" in user_input_lower:
        article = match_article_by_title(user_input, articles)
        if article:
            return f"📜 **Full Article:**\n\n{article['text'][:2000]}..."  # Truncate if needed
        else:
            return "❌ Sorry, no article found to show full content."

    # Case 4: Related articles
    if "related" in user_input_lower or "similar" in user_input_lower:
        topic = extract_topic(user_input)
        headlines = find_related_headlines(topic, vectorstore)
        if headlines:
            return "🧠 **Related Headlines:**\n" + "\n".join([f"- [{t}]({u})" for t, u in headlines])
        return "❌ No related headlines found."

    # Case 5: General question (RAG)
    return answer_question(user_input, vectorstore)


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