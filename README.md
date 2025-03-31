
# AI_News_Assistant


#  NewsGenAI

NewsGenAI is an AI-powered news assistant that enables users to interactively query the latest articles from CBC News using a chatbot interface. It integrates RAG, Web Crawling, and OpenAI’s GPT-4o to deliver accurate, real-time answers and summaries based on up-to-date news content.

Built for researchers, journalists, and news consumers, NewsGenAI automates news scraping, indexing, and intelligent querying. Its modular design ensures fast deployment and easy customization for other publishers or use cases.
## Features
-  RAG-Based QA : Leverages FAISS and GPT-4o to deliver precise, contextually grounded answers based on the latest CBC News articles.
-  Intelligent web scraper for extracting real-world news : Uses Playwright and BeautifulSoup to extract and update full news articles from CBC.
-  Summarization & Headline Generation : AI-Driven Summarization & Headlines: Generates concise article summaries and SEO-optimized headlines with GPT-4. 


##  Quickstart

```bash
git clone https://github.com/rsade090/AI_News_Assistant.git
cd AI_News_Assistant
pip install -r requirements.txt
streamlit run app.py
