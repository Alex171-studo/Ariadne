from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from prompts import RAG_PROMPT_TEMPLATE
from config import model, embedding_model, DATABASE_DIR, DOCS_DIR
from dotenv import load_dotenv

load_dotenv(override=True)

class RAGEngine:
    def __init__(self):
        self.embedding_model = embedding_model
        self.openai_model_name = model
        self.database_path = DATABASE_DIR

        self.embeddings = OpenAIEmbeddings(model=self.embedding_model)
        self.llm = ChatOpenAI(model=self.openai_model_name, temperature=0)

        if os.path.exists(self.database_path) and os.listdir(self.database_path):
            self.database = Chroma(
                persist_directory=self.database_path,
                embedding_function=self.embeddings,
                collection_name="code_query",
            )
        else:
            self.database = self.ingest_docs()

    def ingest_docs(self) -> Chroma:
        loader = DirectoryLoader(
            path=DOCS_DIR,
            glob="*.md",  
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
            show_progress=True,
        )

        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
        )

        chunks = text_splitter.split_documents(documents)

        db = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.database_path,
            collection_name="code_query"
        )
        return db
    
    def query(self, user_question: str) -> str:
        matching_docs = self.database.similarity_search(
            query=user_question,
            k=5,
        )

        context_text = "\n\n".join([doc.page_content for doc in matching_docs])
        chain = RAG_PROMPT_TEMPLATE | self.llm 

        response = chain.invoke({
            "context": context_text,
            "question": user_question
        })

        return response.content