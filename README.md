# AI_News_Assistant

# 📰 NewsGenAI

A modular AI-powered assistant that ingests raw news content, summarizes it using advanced NLP models, and optimizes it for discoverability using SEO analytics. Built to support editorial teams, journalists, and digital content strategists.

## 🔧 Features
- 🧠 GPT-4 + RAG-based summarization
- 📝 Headline optimization using prompt engineering + BART
- 📈 SEO keyword ranking and readability scoring
- 🌐 Intelligent web scraper for extracting real-world news
- 🛡️ Guardrails for hallucination/toxicity detection
- 📊 Streamlit dashboard for demo and rapid testing

## 📦 Tech Stack
- Python · OpenAI GPT-4 · LangChain · FAISS
- HuggingFace · Streamlit · BeautifulSoup · newspaper3k
- Spacy · KeyBERT · Guardrails.ai · Docker

## 🧪 Quickstart

```bash
git clone https://github.com/yourusername/newsgenai.git
cd newsgenai
pip install -r requirements.txt
streamlit run app.py
