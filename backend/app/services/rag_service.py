from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
import time
import json
from langchain_core.output_parsers import JsonOutputParser
from rapidfuzz import process
import json
from langchain_core.prompts import ChatPromptTemplate
import re
from dotenv import load_dotenv

load_dotenv()

class RAGService:

    def __init__(self):
        print("Loading RAG Service Components...")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        self.vector_db_path = "vector_stores"
        os.makedirs(self.vector_db_path, exist_ok=True)

        # FIX: Passing the variable api_key, not the string "api_key"
        api_key = os.getenv("GROQ_API_KEY")

        self.llm = ChatGroq(
            temperature=0, 
            groq_api_key=api_key, 
            model_name="llama-3.1-8b-instant"
        )

        self._index_cache = {} 


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
        """Strictly detects if multiple unique names exist."""
        if not all_metadata or len(all_metadata) <= 1:
            return 100, []

        # Get unique names, ignoring N/A
        unique_names = set()
        for p in all_metadata:
            name = p.get("name", "").strip().upper()
            if name and name != "N/A" and "SAMPLE" not in name:
                unique_names.add(name)
        
        reasons = [f"Found {len(unique_names)} different patient names: {', '.join(unique_names)}"]
        # If more than 1 real name exists, score is 0 (Absolute Mismatch)
        score = 0 if len(unique_names) > 1 else 100
        return score, reasons
    

    def query_report(self, question: str, user_id: str, mode: str = "single", report_ids: list = None, all_report_data: list = None):
        
        print(f"\n🚀 [DEPLOYED VERSION: 2026-06-15-V1]")
        print(f"👤 USER: {user_id} | MODE: {mode} | IDs: {report_ids}")

        user_folder = os.path.join(self.vector_db_path, f"user_{user_id}")
        
        if mode == "overview":
            inventory = []
            for r in all_report_data:
                p = r.get('patient_info', {})
                # Ensure ALL report types are joined into one string
                r_types = r.get('report_type', [])
                type_str = ", ".join(r_types) if isinstance(r_types, list) else str(r_types)
                
                inventory.append({
                    "patient": p.get('name', 'N/A'),
                    "id": p.get('patient_id', 'N/A'),
                    "contains": type_str,
                    "doctor": p.get('doctor_name', 'N/A')
                })

            prompt = ChatPromptTemplate.from_template("""
            You are a Clinical Data Auditor. List the vault inventory.

            INVENTORY DATA:
            {inventory}

            STRICT INSTRUCTIONS:
            1. For each entry, list the Patient Name, ID, and EVERYTHING in the 'contains' field.
            2. IDENTITY CHECK: Compare the 'patient' names across all entries. 
            3. If names like 'BASHIR SHAIKH', 'KANTA YADAV', and 'SHAFIQ QURESHI' are all present, you MUST start your response with: 
               "🚨 **CRITICAL WARNING: MULTIPLE PATIENT IDENTITIES DETECTED**."
            4. Explain that cross-report analysis is disabled for safety.
            5. List the reports as an inventory only.
            """)
            
            chain = prompt | self.llm
            response = chain.invoke({"inventory": json.dumps(inventory)})
            return {"answer": response.content, "sources": "Clinical Registry"}




        



        
        # 🟡 MODE 2 & 3: COMPARE / SINGLE (FAISS Context Retrieval)
        all_contexts = []
        
        # Identity Safety Gate for Comparison
        if mode == "compare" and all_report_data:
            score, gaps = self.verify_patient_identity([r['patient_info'] for r in all_report_data])
            if score < 85:
                return {
                    "answer": f"### 🚨 Safety Block\nIdentity Mismatch detected ({score}% confidence). Gaps: {', '.join(gaps)}. Cross-report analysis is disabled for safety.",
                    "sources": "Safety Engine"
                }

        # Context build karein sirf Database ki active IDs ke liye
        for rid in report_ids:
            path = os.path.join(user_folder, f"report_{rid}")
            print("RID:", rid)
            print(f"📂 CLOUD DEBUG: Checking path: {path}")
            print(f"❓ Path Exists?: {os.path.exists(path)}")

            if os.path.exists(path):
                db = FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)

                t_start = time.time()
                
                if path in self._index_cache:
                    print(f"⚡ CACHE HIT: Using in-memory index for {rid[:8]}")
                    db = self._index_cache[path]
                else:
                    print(f"💾 CACHE MISS: Loading from disk for {rid[:8]}")
                    db = FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
                    self._index_cache[path] = db # Save to RAM
                
                print(f"⏱️ DEBUG: FAISS Retrieval Time: {time.time() - t_start:.4f}s")


                docs = db.similarity_search(question, k=3)
                print(f"📄 Found {len(docs)} chunks for path: {path}")
                for i, d in enumerate(docs):
                    # Yeh terminal mein dikhayega ki AI ne kya 'padha'
                    print(f"   [Chunk {i}] Content: {d.page_content[:150]}...")

                print(f"📄 Retrieved Docs from {rid[:5]}: {len(docs)}")

                all_contexts.append(f"\n=== SOURCE REPORT: {rid[:8]} ===\n" + "\n".join([d.page_content for d in docs]))

        context = "\n".join(all_contexts)
        print(f"📏 Final Context Length: {len(context)}")
        if len(context) > 0:
             print(f"🔎 Context Preview: {context[:200]}...")
        # Final AI reasoning prompt
        prompt = ChatPromptTemplate.from_template("""
        You are a Clinical Data Specialist. Answer based ONLY on the context below.
        
        CONTEXT:
        {context}
        
        QUESTION:
        {question}

        STRICT CLINICAL PROTOCOL:
        1. Never compare different markers (e.g. Glucose vs Hemoglobin).
        2. Strictly ignore reference ranges as results.
        3. Answer in professional Hinglish/English.
        """)

        chain = prompt | self.llm
        response = chain.invoke({"context": context, "question": question})
        
        return {
            "answer": response.content, 
            "sources": f"Analyzed {len(report_ids)} active documents"
        }

    

    def extract_patient_metadata(self, text: str):
    # ----------------------------
    # Regex fallback
    # ----------------------------
        name_match = re.search(
            r"Patient\s*Name\s*[:\-]?\s*([A-Za-z.\s]+)",
            text,
            re.IGNORECASE,
        )

        id_match = re.search(
            r"Patient\s*ID\s*[:\-]?\s*(\d+)",
            text,
            re.IGNORECASE,
        )

        prompt = ChatPromptTemplate.from_template("""
    You are a JSON extraction API.

    Rules:
    1. Return ONLY one valid JSON object.
    2. Do NOT use markdown.
    3. Do NOT wrap inside ```json.
    4. Do NOT explain anything.
    5. If information is missing, return "N/A".
    6. Preserve values exactly as written in the report.

    Return exactly:

    {{
        "name": "",
        "age": "",
        "gender": "",
        "date_of_birth": "",
        "patient_id": "",
        "doctor_name": "",
        "hospital_name": "",
        "sample_type": ""
    }}

    Report Text:
    {text}
    """)

        chain = prompt | self.llm

        response = chain.invoke({
            "text": text
        })

        print("\n" + "=" * 60)
        print("🔍 RAW LLM METADATA RESPONSE")
        print(response.content)
        print("=" * 60 + "\n")

        try:

            match = re.search(r"\{.*\}", response.content, re.DOTALL)

            if not match:
                raise ValueError("No JSON object found.")

            metadata = json.loads(match.group(0))

            # ----------------------------
            # Normalize empty values
            # ----------------------------
            for key in [
                "name",
                "age",
                "gender",
                "date_of_birth",
                "patient_id",
                "doctor_name",
                "hospital_name",
                "sample_type",
            ]:
                value = str(metadata.get(key, "")).strip()

                if value == "":
                    metadata[key] = "N/A"
                else:
                    metadata[key] = value

            # ----------------------------
            # Regex fallback
            # ----------------------------
            if metadata["name"] == "N/A" and name_match:
                metadata["name"] = name_match.group(1).strip()

            if metadata["patient_id"] == "N/A" and id_match:
                metadata["patient_id"] = id_match.group(1).strip()

            # ----------------------------
            # Doctor cleanup
            # ----------------------------
            doctor = metadata["doctor_name"].strip()

            blocked_exact = {
                "main lab",
                "diagnostic centre",
                "diagnostic center",
                "laboratory",
                "hospital",
                "clinic",
            }

            if doctor.lower() in blocked_exact:
                metadata["doctor_name"] = "N/A"

            print("✅ Parsed metadata:", metadata)
            print("👨‍⚕️ Doctor extracted:", metadata.get("doctor_name"))

            return metadata

        except Exception as e:

            print(f"❌ Metadata Extraction Error: {e}")

            return {
                "name": "N/A",
                "age": "N/A",
                "gender": "N/A",
                "date_of_birth": "N/A",
                "patient_id": "N/A",
                "doctor_name": "N/A",
                "hospital_name": "N/A",
                "sample_type": "N/A",
            }
# Singleton instance
rag_service = RAGService()