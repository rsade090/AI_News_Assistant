
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
from newspaper import Article

BASE_URL = "https://www.cbc.ca"

def extract_article_text(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.title, article.text
    except:
        return None, None


def get_cbc_articles(limit=10):
    print("Crawling CBC homepage...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                args=["--disable-blink-features=AutomationControlled"]
            )
            context = browser.new_context(user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0.0.0 Safari/537.36"
            ))
            page = context.new_page()
            page.goto("https://www.cbc.ca/news", timeout=60000, wait_until="networkidle")
            html = page.content()
            browser.close()
    except Exception as e:
        print(f"[ERROR] Failed to crawl CBC: {e}")
        return []

    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", href=True)

    articles = []
    visited = set()

    for link in links:
        href = link["href"]
        if '/news/' in href and href.count('-') >= 2 and not any(x in href for x in ['/video/', '/live/', '/audio/']):
            full_url = urljoin(BASE_URL, href)
            if full_url in visited:
                continue
            visited.add(full_url)
            title, text = extract_article_text(full_url)
            if title and text and len(text) > 300:
                articles.append({
                    "title": title.strip(),
                    "url": full_url.strip(),
                    "text": text.strip()
                })
            if len(articles) >= limit:
                break

    print(f"Collected {len(articles)} full articles.")
    return articles


