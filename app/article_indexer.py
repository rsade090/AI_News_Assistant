import os
import json
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document
from dotenv import load_dotenv
from app.cbc_crawler import get_articles
from pathlib import Path

load_dotenv()
embedding_model = OpenAIEmbeddings()


INDEX_PATH = "vectorstore/index.faiss"
METADATA_PATH = "vectorstore/articles.json"

def index_articles(articles: List[Dict[str, str]], chunk_size=300):
    print(f"Indexing {len(articles)} articles...")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=50)
    docs = []
    metadata_list = []

    for article in articles:
        chunks = text_splitter.split_text(article['text'])
        for chunk in chunks:
            docs.append(Document(page_content=chunk, metadata={"title": article["title"], "url": article["url"]}))
        metadata_list.append({
            "title": article["title"],
            "url": article["url"],
            "text": article["text"]
        })

    # Ensure the directory for the vectorstore exists
    vectorstore_dir = Path(INDEX_PATH).parent
    vectorstore_dir.mkdir(parents=True, exist_ok=True)

    try:
        vectorstore = FAISS.from_documents(docs, embedding_model)
        vectorstore.save_local(INDEX_PATH)
        print(f"[INFO] Vectorstore saved at {INDEX_PATH}.")
    except Exception as e:
        print(f"[ERROR] Failed to save vectorstore: {e}")
        raise e

    try:
        with open(METADATA_PATH, "w", encoding="utf-8") as f:
            json.dump(metadata_list, f, indent=2)
        print(f"[INFO] Metadata saved at {METADATA_PATH}.")
    except Exception as e:
        print(f"[ERROR] Failed to save metadata: {e}")
        raise e

    print(f"Indexed {len(docs)} chunks from {len(articles)} articles.")

def fetch_and_index_articles():
    print("[INFO] Fetching articles from CBC...")
    articles = get_articles()
    if articles:
        index_articles(articles)
    else:
        print("[WARNING] No articles fetched. Skipping indexing.")
        # create an empty vectorstore to avoid breaking the app
        vectorstore_dir = Path(INDEX_PATH).parent
        vectorstore_dir.mkdir(parents=True, exist_ok=True)
        FAISS.from_documents([], embedding_model).save_local(INDEX_PATH)
        print("[INFO] Created an empty vectorstore as a fallback.")

def load_metadata() -> List[Dict[str, str]]:

    if not os.path.exists(METADATA_PATH):
        print("[WARNING] Metadata file not found. Returning an empty list.")
        return []
    
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_vectorstore(refresh=False) -> FAISS:
    """
    If the vectorstore file is missing or `refresh` is True, fetch and index articles.
    """
    if refresh or not Path(INDEX_PATH).exists():
        print(f"[Warning] Vectorstore file not found at {INDEX_PATH}. Attempting to create it...")
        try:
            fetch_and_index_articles()  
        except Exception as e:
            raise FileNotFoundError(f"[Error] Failed to create vectorstore file at {INDEX_PATH}. Details: {e}")
    
    if not Path(INDEX_PATH).exists():
        raise FileNotFoundError(f"[Warning] Vectorstore file still not found at {INDEX_PATH}.")
    
    print(f"[INFO] Loading vectorstore from {INDEX_PATH}...")
    try:
        vectorstore = FAISS.load_local(
            INDEX_PATH,
            embedding_model,
            allow_dangerous_deserialization=True
        )
        print("[INFO] Successfully loaded vectorstore.")
        return vectorstore
    except Exception as e:
        print(f"[ERROR] Failed to load vectorstore: {e}")
        raise e