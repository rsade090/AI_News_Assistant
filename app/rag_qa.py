import os
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# Initialize GPT-4o model
llm = ChatOpenAI(model_name="gpt-4o", temperature=0.6)

# Prompt template
QA_TEMPLATE = """
You are a helpful assistant to report the lates news and answers questions 
    based on the provided context from CBC news articles. Respond naturally and 
    you are reporting the news as an expert journalism/reporter. 
    Avoid mentioning the context explicitly unless necessary.
    Do not create fake news or provide false information. If possible, answer in markdown format so that
    the user can easily catch the gist of the answer.

Context:
{context}

Question:
{question}

Answer:
"""

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=QA_TEMPLATE
)


def answer_question(query: str, vectorstore) -> str:
    """
    Answer a question using the provided vectorstore.
    """
    try:
        # Create a retriever from the provided vectorstore
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

        # Create a new RAG chain with the retriever
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=False,
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt}
        )

        # Run the query through the RAG chain
        result = qa_chain.run(query)
        return f"\n{result}"
    except Exception as e:
        return f"❌ Error answering question: {e}"