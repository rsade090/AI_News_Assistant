from bs4 import BeautifulSoup
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
import requests

BASE_URL = "https://www.cbc.ca"

def get_article_links(url="https://www.cbc.ca/news", headless=True):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        all_links = soup.find_all('a', href=True)

        article_urls = set()
        for link in all_links:
            href = link['href']
            if (
                '/news/' in href
                and href.count('-') >= 2
                and not href.endswith('/news')
                and not any(x in href for x in ['/video/', '/live/', '/audio/'])
            ):
                full_url = urljoin(BASE_URL, href)
                article_urls.add(full_url)

        return sorted(article_urls)
    except Exception as e:
        print(f"[ERROR] Failed to fetch article links: {e}")
        return []

def fetch_article_content(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        content = soup.find("div", class_="story").get_text(strip=True)
        return content
    except Exception as e:
        print(f"[ERROR] Failed to fetch content for {url}: {e}")
        return None

def get_articles(url="https://www.cbc.ca/news", headless=True, limit=20):
    
    article_links = get_article_links(url, headless)
    
    print(f"[INFO] Found {len(article_links)} article links.")
    articles = []
    for i, link in enumerate(article_links[:limit]):
        print(f"[INFO] Fetching article {i + 1}/{limit}: {link}")
        content = fetch_article_content(link)
        if content:
            articles.append({"title": link.split("/")[-1], "url": link, "text": content})
    return articles