from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

class RAGService:
    def __init__(self):
        print("Loading RAG Service Components...")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=250)
        self.vector_db_path = "vector_stores"
        os.makedirs(self.vector_db_path, exist_ok=True)

        # FIX: Passing the variable api_key, not the string "api_key"
        api_key = os.getenv("GROQ_API_KEY")

        self.llm = ChatGroq(
            temperature=0, 
            groq_api_key=api_key, 
            model_name="llama-3.1-8b-instant"
        )

    def index_report(self, text: str, user_id: str):
        """Chunks and stores the report in FAISS."""
        chunks = self.text_splitter.split_text(text)
        user_db_path = os.path.join(self.vector_db_path, f"user_{user_id}")
        db = FAISS.from_texts(chunks, self.embeddings)
        db.save_local(user_db_path)
        return len(chunks)

    def query_report(self, question: str, user_id: str):
        """Retrieves context and generates an AI answer."""
        user_db_path = os.path.join(self.vector_db_path, f"user_{user_id}")

        if not os.path.exists(user_db_path):
            return {
                "answer": "No report found. Please upload a PDF first.",
                "sources": ""
            }

        # Load the index
        db = FAISS.load_local(user_db_path, self.embeddings, allow_dangerous_deserialization=True)

        # Search for top 3 matches
        relevant_docs = db.similarity_search(question, k=3)
        context = "\n".join([doc.page_content for doc in relevant_docs])

        prompt = ChatPromptTemplate.from_template("""
        You are an AI Medical Assistant. Use the provided context to answer the user's question.
        Guidelines:
        1. Be concise and professional.
        2. If the answer is not in the context, say: "This information is not available in the uploaded report."
        3. Do not make up medical facts.
        
        Context: {context}
        Question: {question}
        
        Answer:
        """)

        chain = prompt | self.llm
        response = chain.invoke({"context": context, "question": question})
        
        return {
            "answer": response.content,
            "sources": context
        }


    def extract_patient_metadata(self, text: str):
        """Uses Llama 3.1 to extract structured patient details from raw text."""
        prompt = ChatPromptTemplate.from_template("""
        Extract patient details from this medical text in JSON format. 
        Fields: name, age, gender, patient_id, doctor_name, hospital_name, sample_type.
        If a field is missing, use "N/A". Return ONLY the raw JSON.

        Text: {text}
        """)
        
        chain = prompt | self.llm
        response = chain.invoke({"text": text[:2000]}) # Sending only first 2k chars for speed
        
        # Simple cleanup to ensure valid JSON
        try:
            import json
            # Finding the JSON block in case LLM adds extra text
            start = response.content.find('{')
            end = response.content.rfind('}') + 1
            return json.loads(response.content[start:end])
        except:
            return {"name": "Unknown", "age": "N/A"}


# Singleton instance
rag_service = RAGService()