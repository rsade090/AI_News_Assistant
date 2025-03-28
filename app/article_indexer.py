import os
import json
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document
from dotenv import load_dotenv
from app.cbc_crawler import get_articles

load_dotenv()
embedding_model = OpenAIEmbeddings()

# Where we'll save data
INDEX_PATH = "vectorstore/index.faiss"
METADATA_PATH = "vectorstore/articles.json"

def index_articles(articles: List[Dict[str, str]], chunk_size=300):
    print(f"🔄 Indexing {len(articles)} articles...")

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

    # Embed and store
    try:
        vectorstore = FAISS.from_documents(docs, embedding_model)
        vectorstore.save_local(INDEX_PATH)
        print(f"[INFO] Vectorstore saved at {INDEX_PATH}.")
    except Exception as e:
        print(f"[ERROR] Failed to save vectorstore: {e}")
        raise e

    # Save metadata
    try:
        with open(METADATA_PATH, "w", encoding="utf-8") as f:
            json.dump(metadata_list, f, indent=2)
        print(f"[INFO] Metadata saved at {METADATA_PATH}.")
    except Exception as e:
        print(f"[ERROR] Failed to save metadata: {e}")
        raise e

    print(f"✅ Indexed {len(docs)} chunks from {len(articles)} articles.")

def fetch_and_index_articles():
    print("[INFO] Fetching articles from CBC...")
    articles = get_articles()
    if articles:
        index_articles(articles)
    else:
        print("[WARNING] No articles fetched.")


def load_metadata() -> List[Dict[str, str]]:
    """
    Load the metadata of indexed articles from the JSON file.
    """
    if not os.path.exists(METADATA_PATH):
        print("[WARNING] Metadata file not found. Returning an empty list.")
        return []
    
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_vectorstore(refresh=False) -> FAISS:
    """
    Load the FAISS vectorstore from the saved index file.
    If the vectorstore file is missing or `refresh` is True, fetch and index articles.
    """
    if refresh or not os.path.exists(INDEX_PATH):
        print("[INFO] Vectorstore file not found or refresh requested. Indexing articles now...")
        fetch_and_index_articles()  # Automatically fetch and index articles
        if not os.path.exists(INDEX_PATH):
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