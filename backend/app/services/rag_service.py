from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os

class RAGService:
    def __init__(self):
        # 1. Load the 'Researcher' (Embeddings)
        print("Loading RAG Embedding Model...")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=250)
        self.vector_db_path = "vector_stores"
        os.makedirs(self.vector_db_path, exist_ok=True)

        # 1. Initialize Groq LLM (Put your API Key in .env later)
        # Model 'llama3-8b-8192' is free and very smart
        self.llm = ChatGroq(
            temperature=0, 
            groq_api_key="APKA_GROQ_API_KEY_YAHAN_DALEIN", 
            model_name="llama3-8b-8192"
        )
    def query_report(self, question: str, user_id: str):
        user_db_path = os.path.join(self.vector_db_path, f"user_{user_id}")
        if not os.path.exists(user_db_path):
            return "No report found."

        db = FAISS.load_local(user_db_path, self.embeddings, allow_dangerous_deserialization=True)
        relevant_docs = db.similarity_search(question, k=3)
        context = "\n".join([doc.page_content for doc in relevant_docs])

        # 2. Industry Standard: The Prompt Template
        # Hum LLM ko 'Acting' sikhate hain
        prompt = ChatPromptTemplate.from_template("""
        You are a professional Medical Assistant. Answer the question based ONLY on the provided context.
        If the answer is not in the context, say "I don't find this information in the report."
        
        Context: {context}
        Question: {question}
        
        Answer:
        """)

        # 3. Chain create karein aur answer generate karein
        chain = prompt | self.llm
        response = chain.invoke({"context": context, "question": question})
        
        return response.content

    def index_report(self, text: str, user_id: str):
        """
        Report text ko chunks mein tod kar Vector DB mein save karna.
        """
        chunks = self.text_splitter.split_text(text)
        
        # Har user ka apna folder hoga (Industry Standard for Privacy)
        user_db_path = os.path.join(self.vector_db_path, f"user_{user_id}")
        
        # Create Vector Store
        db = FAISS.from_texts(chunks, self.embeddings)
        db.save_local(user_db_path)
        
        return len(chunks)

    def query_report(self, question: str, user_id: str):
        """
        Database se sawaal ka jawab dhoondna.
        """
        user_db_path = os.path.join(self.vector_db_path, f"user_{user_id}")
        
        if not os.path.exists(user_db_path):
            return "No report found. Please upload a report first."

        # Load the user's specific memory
        db = FAISS.load_local(user_db_path, self.embeddings, allow_dangerous_deserialization=True)
        
        # Dhoondna: Sawaal se milte-julte top 3 chunks
        relevant_docs = db.similarity_search(question, k=3)
        context = "\n".join([doc.page_content for doc in relevant_docs])

        # Note: Abhi hum sirf 'Context' return kar rahe hain. 
        # Agle step mein hum ise Claude/GPT API ko bhejenge 'Generation' ke liye.
        return context

# Singleton instance
rag_service = RAGService()