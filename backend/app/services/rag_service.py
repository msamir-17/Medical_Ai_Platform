from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
from langchain_core.output_parsers import JsonOutputParser


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

    def index_report(self, text: str, user_id: str, report_id: str):
        chunks = self.text_splitter.split_text(text)
        
        # 1. Save Specific Report Index (Existing Logic)
        report_path = os.path.join(self.vector_db_path, f"user_{user_id}", f"report_{report_id}")
        os.makedirs(report_path, exist_ok=True)
        db = FAISS.from_texts(chunks, self.embeddings)
        db.save_local(report_path)

        # 2. THE FIX: Create/Update Master User Index
        master_path = os.path.join(self.vector_db_path, f"user_{user_id}", "master_index")
        os.makedirs(master_path, exist_ok=True)
        
        if os.path.exists(os.path.join(master_path, "index.faiss")):
            # If master exists, add new report chunks to it
            master_db = FAISS.load_local(master_path, self.embeddings, allow_dangerous_deserialization=True)
            master_db.add_texts(chunks)
            master_db.save_local(master_path)
        else:
            # First report? Create the master index
            db.save_local(master_path)
            
        print(f"✅ MASTER INDEX UPDATED at {master_path}")
        return len(chunks)

    def classify_query(self, question: str):
        """
        Senior Logic: Decisions whether to use Structured Data (SQL) or Unstructured (RAG).
        """
        prompt = ChatPromptTemplate.from_template("""
        Analyze the user's medical question and categorize it into ONE of these:
        1. "NUMERIC": Question is about a specific lab value (e.g., What is my glucose?)
        2. "EXPLANATION": Question asks WHY a value is high/low or what it means.
        3. "SUMMARY": User wants a summary of the report.
        4. "GENERAL": Anything else (Doctor name, hospital, etc.)

        Return ONLY a JSON object like this: {{"category": "CATEGORY_NAME", "target_marker": "marker_name_if_any"}}
        
        Question: {question}
        """)
        
        chain = prompt | self.llm | JsonOutputParser()
        try:
            return chain.invoke({"question": question})
        except:
            # FIX: Use empty string instead of None
            return {"category": "GENERAL", "target_marker": ""}

    def query_report(self, question: str, user_id: str, report_id: str = None, db_report_data: dict = None):
        """
        The Router Logic: Routes the question to the best data source.
        """
        # 1. Decide Path and System Role
        if report_id and report_id != "":
            path = os.path.join(self.vector_db_path, f"user_{user_id}", f"report_{report_id}")
        else:
            path = os.path.join(self.vector_db_path, f"user_{user_id}", "master_index")

        if not os.path.exists(path):
            return {"answer": "I don't have these reports in my memory yet. Please re-upload.", "sources": ""}


        # 2. Classify the intent (Numerical vs General)
        intent = self.classify_query(question)
        category = intent.get("category", "GENERAL")
        marker_raw = intent.get("target_marker", "")
        marker = marker_raw.lower() if marker_raw else ""

        # 3. ROUTE A: Numeric Data (Source: Postgres/Supabase)
        if category == "NUMERIC" and db_report_data:
            for item in db_report_data.get("extracted_values", []):
                if marker in item['marker'].lower() or item['marker'].lower() in marker:
                    return {
                        "answer": f"Your {item['marker']} level is {item['value']} {item['unit']}. This is considered {item['status']}.",
                        "sources": "Structured Database (PostgreSQL)"
                    }

        # 4. ROUTE B: Semantic Search (Source: FAISS)
        # Note: We use the 'path' defined in Step 1 (No redundant overwriting)
        if not os.path.exists(path):
            return {"answer": "Context not found. Please ensure reports are uploaded.", "sources": ""}

        # Load the correct index (Specific or Master)
        db = FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
        relevant_docs = db.similarity_search(question, k=6)
        context_parts = []
        for doc in relevant_docs:
            source = doc.metadata.get("report_id", "Unknown Report")
            context_parts.append(f"[SOURCE: {source}]\n{doc.page_content}")
        
        context = "\n---\n".join(context_parts)

        prompt = ChatPromptTemplate.from_template("""
        You are a Senior Medical AI Consultant. You are analyzing a patient's medical history.

        CONTEXT:
        {context}
        
        QUESTION:
        {question}

        STRICT CLINICAL RULES:
        1. Only answer based on ACTUAL results. Ignore reference examples.
        2. If a report is labeled as a "Sample" or has a mismatching ID, flag it as a 🚨 **Conflict**.
        3. Use simple Hinglish/English.

        --- 
        PROFESSIONAL FORMATTING RULES (MANDATORY):
        1. Use **Markdown Headers (##)** for major sections.
        2. Use **Bold text** for medical markers (e.g., **Glucose**, **HbA1c**).
        3. Use a **Markdown Table** to compare lab values if they appear in multiple reports.
        4. Use 🩺 for 'Executive Summary' and 🚨 for 'High-Priority Warnings'.
        5. Use a clear **Longitudinal Health Timeline** at the end.
        ---

        Answer:
        """)

        chain = prompt | self.llm
        response = chain.invoke({
            "context": context, 
            "question": question
        })
        
        return {
            "answer": response.content, 
            "sources": "Master Knowledge Base" if not report_id else "Specific Report"
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