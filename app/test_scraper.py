from scraper import extract_article_text

url = "https://www.cbc.ca/news"  
text = extract_article_text(url)
print(text)  # Print the first 1000 characters
