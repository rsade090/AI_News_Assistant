import streamlit as st
from app.intent_router import route_user_query
from app.article_indexer import load_vectorstore, load_metadata



st.set_page_config(page_title="NewsGenAI", layout="wide")

if "vectorstore_initialized" not in st.session_state:
    try:
        st.session_state["vectorstore"] = load_vectorstore(refresh=True)  # Refresh on first startup
        st.session_state["articles"] = load_metadata()  
        st.session_state["vectorstore_initialized"] = True
        st.success("Vectorstore and metadata initialized with the latest news.")
    except FileNotFoundError as e:
        st.error("Vectorstore or metadata not found and could not be created. Please check the logs.")
        st.error(f"Error details: {e}")
        st.stop()

vectorstore = st.session_state["vectorstore"]
articles = st.session_state["articles"]

st.title(" NewsGenAI — CBC News Chatbot")

if st.button("Refresh News Data"):
    with st.spinner("Refreshing news data..."):
        from app.article_indexer import fetch_and_index_articles
        fetch_and_index_articles()
        st.session_state["vectorstore"] = load_vectorstore(refresh=False)  # Reload the updated vectorstore
        st.session_state["articles"] = load_metadata()  
        st.success("News data refreshed. Please restart the app.")


if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(f" {msg['content']}")

user_query = st.chat_input("Ask me about CBC News...")

if "streamed_response" not in st.session_state:
    st.session_state["streamed_response"] = ""

if user_query:
    st.session_state["messages"].append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(f"{user_query}")

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        st.session_state["streamed_response"] = ""

        def stream_to_ui(token: str):
            st.session_state["streamed_response"] += token
            response_placeholder.markdown(
                st.session_state["streamed_response"],
                unsafe_allow_html=True
            )

        with st.spinner("Thinking..."):
            route_user_query(
                user_query,
                articles,
                vectorstore,
                stream_function=stream_to_ui
            )

        st.session_state["messages"].append({
            "role": "assistant",
            "content": st.session_state["streamed_response"]
        })