from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
from langchain_core.output_parsers import JsonOutputParser
from rapidfuzz import process

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

        # --- THE FIX: ADD METADATA TO EVERY CHUNK ---
        metadatas = [{"report_id": report_id, "user_id": user_id} for _ in chunks]
        
        # 1. Save Specific Report Index (Existing Logic)
        report_path = os.path.join(self.vector_db_path, f"user_{user_id}", f"report_{report_id}")
        os.makedirs(report_path, exist_ok=True)
        db = FAISS.from_texts(chunks, self.embeddings, metadatas=metadatas)
        db.save_local(report_path)

        # 2. THE FIX: Create/Update Master User Index
        master_path = os.path.join(self.vector_db_path, f"user_{user_id}", "master_index")
        os.makedirs(master_path, exist_ok=True)
        
        if os.path.exists(os.path.join(master_path, "index.faiss")):
            # If master exists, add new report chunks to it
            master_db = FAISS.load_local(master_path, self.embeddings, allow_dangerous_deserialization=True)
            master_db.add_texts(chunks,metadatas=metadatas)
            master_db.save_local(master_path)
        else:
            # First report? Create the master index
            db.save_local(master_path)            
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
    
    def verify_patient_identity(self, all_metadata: list):
        """Calculates if all reports belong to the same person."""
        if not all_metadata or len(all_metadata) <= 1:
            return 100, ""

        score = 0
        base = all_metadata[0]
        reasons = []

        for other in all_metadata[1:]:
            # 1. Patient ID Check
            if base.get("patient_id") == other.get("patient_id") and base.get("patient_id") != "N/A":
                score += 60
            
            # 2. Name Similarity (Using rapidfuzz)
            name_match = process.extractOne(base.get("name", ""), [other.get("name", "")])
            if name_match and name_match[1] > 85:
                score += 25
            else:
                reasons.append(f"Names differ: {base.get('name')} vs {other.get('name')}")

            # 3. Gender Check
            if base.get("gender") == other.get("gender"):
                score += 15
            else:
                reasons.append("Gender mismatch detected")

        avg_score = score / (len(all_metadata) - 1)
        return avg_score, reasons

    def query_report(self, question: str, user_id: str, mode: str = "single", report_ids: list = None, all_patient_info: list = None):
        user_folder = os.path.join(self.vector_db_path, f"user_{user_id}")
        all_contexts = []
        
        # --- 1. IDENTITY & SAFETY GATE (Trigger for Multi-report modes) ---
        identity_warning = ""
        if mode in ["compare", "overview"] and all_patient_info and len(all_patient_info) > 1:
            score, gaps = self.verify_patient_identity(all_patient_info)
            if score < 85:
                return {
                    "answer": f"### ⚠️ Clinical Safety Block\nIdentity mismatch detected (Score: {score}%).\n**Gaps:** {', '.join(gaps)}\n\nPlease select reports belonging to the same person.",
                    "sources": "Safety Engine"
                }

        # --- 2. DYNAMIC PATH IDENTIFICATION (The "List-to-String" Fix) ---
        if mode == "overview":
            # Sabhi available report folders dhundo
            if not os.path.exists(user_folder):
                 return {"answer": "No records found.", "sources": ""}
            paths_to_search = [os.path.join(user_folder, d) for d in os.listdir(user_folder) if d.startswith("report_")]
        else:
            # Single ya Compare mode: Use the IDs provided
            # FIX: Iterate through list instead of putting list in a string
            paths_to_search = [os.path.join(user_folder, f"report_{rid}") for rid in report_ids if rid]

        # --- 3. CONTEXT RETRIEVAL (Fetching real text from FAISS) ---
        for path in paths_to_search:
            if os.path.exists(path):
                db = FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
                # Har report se top 3 relevant chunks lo
                docs = db.similarity_search(question, k=3)
                report_label = path.split("report_")[-1][:8]
                all_contexts.append(f"\n[DATA FROM REPORT ID: {report_label}]\n" + "\n".join([d.page_content for d in docs]))

        context = "\n".join(all_contexts)
        if not context.strip():
            return {"answer": "I found the files, but they contain no readable text. Please re-upload.", "sources": "OCR Check"}

        # --- 4. THE MASTER PROMPT ---
        prompt = ChatPromptTemplate.from_template("""
        You are a Clinical Data Integrity Agent. 
        
        CONTEXT:
        {context}
        
        USER QUESTION:
        {question}

        STRICT CLINICAL PROTOCOL:
        1. Only use values listed under "Result" or "Value". 
        2. STRICTLY IGNORE reference ranges (e.g., 11.0-16.0) as patient results.
        3. If multiple reports are present, summarize them report-by-report.
        4. Use Markdown for structured output (headers, bold, tables).

        Answer:
        """)

        chain = prompt | self.llm
        response = chain.invoke({"context": context, "question": question})
        
        return {
            "answer": response.content, 
            "sources": f"Analyzed {len(paths_to_search)} clinical records"
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