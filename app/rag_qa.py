import os
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain.callbacks.base import BaseCallbackHandler

class StreamToAppCallbackHandler(BaseCallbackHandler):
    def __init__(self, stream_function):

        self.stream_function = stream_function

    def on_llm_new_token(self, token: str, **kwargs) -> None:

        self.stream_function(token)  

load_dotenv()

llm = ChatOpenAI(model_name="gpt-4o", temperature=0.6, streaming=True)

def add_Articles(articles):
 
    titles = "\n".join([f"- {article['title']}" for article in articles])
    sys_prompt = (
        "You are a helpful assistant to report the latest news and answer questions "
        "based on the provided context from CBC news articles. Respond naturally and "
        "you are reporting the news as an expert journalist/reporter. "
        "Do not create fake news or provide false information. If possible, answer in markdown format so that "
        "the user can easily catch the gist of the answer. "
        "You have access to the following article titles:\n\n"
        f"{titles}\n\n"
    )
    return sys_prompt

def create_QA_template(articles):

    return add_Articles(articles) + """


Context:
{context}

Question:
{question}

Answer:
"""

def answer_question(query: str, vectorstore, articles: list, stream_function=None):

    try:
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

        QA_TEMPLATE = create_QA_template(articles)

        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=QA_TEMPLATE
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=False,
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt}
        )

        if stream_function:
            
            qa_chain.run(query, callbacks=[StreamToAppCallbackHandler(stream_function)])
            return ""  # No need to return the full response since it's streamed
        else:
            # Run the query and return the full response
            result = qa_chain.run(query)
            return f"\n{result}"
    except Exception as e:
        return f" Error answering question: {e}"