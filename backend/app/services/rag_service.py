import sys
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
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
from datetime import datetime
import re
from dotenv import load_dotenv

load_dotenv()

def filter_by_l2_threshold(retrieved_results_with_scores, threshold: float = 1.3, query: str = ""):
    filtered_docs = [doc for doc, score in retrieved_results_with_scores if score <= threshold]
    
    keywords = ["trend", "history", "change"]
    if any(k in query.lower() for k in keywords):
        filtered_docs.sort(key=lambda doc: doc.metadata.get("report_date", "1970-01-01"))
        
    return filtered_docs

def format_abnormal_findings(extracted_values: list) -> str:
    """
    Production-grade clean text formatter for abnormal lab markers.
    Eliminates JSON formatting noise ({}, [], ", :) and token waste by 80%.
    """
    if not extracted_values or not isinstance(extracted_values, list):
        return ""
    
    abnormal_lines = []
    for item in extracted_values:
        if not isinstance(item, dict):
            continue
        status = str(item.get("status", "")).upper()
        if status in ["HIGH", "LOW", "CRITICAL", "ABNORMAL"]:
            marker = item.get("marker", "MARKER")
            val = item.get("value", "")
            unit = item.get("unit", "")
            ref = item.get("ref_range", "")
            abnormal_lines.append(f"- {marker}: {val} {unit} ({status} | Normal Ref: {ref})")
            
    if not abnormal_lines:
        return ""
        
    return "\n🚨 PRE-PARSED CRITICAL & ABNORMAL LAB FINDINGS (FROM DATABASE):\n" + "\n".join(abnormal_lines) + "\n"

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

        # FIX: Load API key and model dynamically
        api_key = os.getenv("GROQ_API_KEY")
        model_name = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

        self.llm = ChatGroq(
            temperature=0, 
            groq_api_key=api_key, 
            model_name=model_name,
            max_tokens=750
        )

        self._index_cache = {} 


    def index_report(self, text: str, user_id: str, report_id: str, extracted_metadata: dict = None):
        if extracted_metadata is None:
            extracted_metadata = {}

        date_str = str(extracted_metadata.get("date", "") or extracted_metadata.get("report_date", "") or extracted_metadata.get("date_of_birth", "")).strip()
        report_date = "1970-01-01"

        if date_str and date_str != "N/A":
            date_formats = [
                "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y",
                "%m-%d-%Y", "%d %b %Y", "%d %B %Y", "%Y/%m/%d"
            ]
            for fmt in date_formats:
                try:
                    report_date = datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
                    break
                except (ValueError, TypeError):
                    continue

        extracted_metadata["report_date"] = report_date

        chunks = self.text_splitter.split_text(text)

        # --- THE FIX: ADD METADATA TO EVERY CHUNK ---
        metadatas = [{"report_id": report_id, "user_id": user_id, "report_date": report_date} for _ in chunks]
        
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
                t_start = time.time()
                
                if path in self._index_cache:
                    print(f"⚡ CACHE HIT: Using in-memory index for {rid[:8]}")
                    db = self._index_cache[path]
                else:
                    print(f"💾 CACHE MISS: Loading from disk for {rid[:8]}")
                    db = FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
                    self._index_cache[path] = db # Save to RAM
                
                # 1. Dense FAISS Vector Search with L2 Threshold Gate
                faiss_results = db.similarity_search_with_score(question, k=6)
                faiss_docs = filter_by_l2_threshold(faiss_results, threshold=1.3, query=question)

                # 2. Sparse BM25 Keyword Search (Ensures exact terms like Creatinine/BUN/Potassium are never missed)
                bm25_docs = []
                try:
                    all_chunks = [doc for doc in db.docstore._dict.values()] if hasattr(db, 'docstore') else faiss_docs
                    if all_chunks:
                        bm25 = BM25Retriever.from_documents(all_chunks)
                        bm25.k = 4
                        bm25_docs = bm25.invoke(question) if hasattr(bm25, 'invoke') else bm25.get_relevant_documents(question)
                except Exception as bm_err:
                    print(f"[BM25 WARNING] Fallback to FAISS: {bm_err}")

                # 3. Ensemble Hybrid Deduplication
                combined_docs = []
                seen_content = set()
                for doc in bm25_docs + faiss_docs:
                    if doc.page_content not in seen_content:
                        seen_content.add(doc.page_content)
                        combined_docs.append(doc)

                print(f"[HYBRID RAG DEBUG] Retrieved {len(combined_docs)} unique docs (BM25 + FAISS)")

                # 4. Clean Abnormal Lab Findings Injector (80% token reduction over raw JSON)
                struct_summary = ""
                if all_report_data:
                    for rep in all_report_data:
                        if rep.get("id") == rid and rep.get("extracted_values"):
                            struct_summary = format_abnormal_findings(rep["extracted_values"])

                report_text_block = "\n".join([d.page_content for d in combined_docs])
                all_contexts.append(f"\n=== SOURCE REPORT: {rid[:8]} ===\n{struct_summary}\n--- EXTRACTED REPORT CONTEXT ---\n" + report_text_block)

        context = "\n".join(all_contexts)
        print(f"[RAG DEBUG] Final Context Length: {len(context)}")
        if len(context) > 0:
             print(f"[RAG DEBUG] Context Preview: {context[:200]}...")
        # Final AI reasoning prompt
        prompt = ChatPromptTemplate.from_template("""
        You are a Clinical Data Specialist. Answer based ONLY on the context below.
        
        CONTEXT:
        {context}
        
        QUESTION:
        {question}

        STRICT CLINICAL PROTOCOL:
        1. Never compare different markers (e.g. Glucose vs Hemoglobin).
        2. Analyze ALL lab sections provided (CBC, KFT/Renal, Urine, ABG).
        3. Clearly highlight critical abnormalities (e.g. Severe Anemia, High Creatinine/BUN, Hyperkalemia).
        4. Answer in professional English.
        """)

        try:
            chain = prompt | self.llm
            response = chain.invoke({"context": context, "question": question})
            answer_text = response.content
        except Exception as groq_err:
            print(f"[RAG ERROR] Groq API timeout/failure: {groq_err}")
            fallback_findings = []
            if all_report_data:
                for rep in all_report_data:
                    if rep.get("extracted_values"):
                        formatted = format_abnormal_findings(rep["extracted_values"])
                        if formatted:
                            fallback_findings.append(formatted)
            if fallback_findings:
                answer_text = "⚠️ **[Groq API Offline Fallback] Direct Database Findings:**\n" + "\n".join(fallback_findings)
            else:
                answer_text = "⚠️ AI reasoning service is currently unavailable. Please try again shortly."

        return {
            "answer": answer_text, 
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

        raw_llm_content = ""
        try:
            # Truncate text to top 2500 characters (header area) to prevent Groq TPM rate limits
            response = chain.invoke({
                "text": text[:2500]
            })
            raw_llm_content = getattr(response, 'content', str(response))
            print("\n" + "=" * 60)
            print("[METADATA LLM] RAW RESPONSE:")
            print(raw_llm_content)
            print("=" * 60 + "\n")
        except Exception as llm_err:
            print(f"[METADATA WARNING] Groq LLM skipped due to rate limit/error: {llm_err}")

        try:
            match = re.search(r"\{.*\}", raw_llm_content, re.DOTALL) if raw_llm_content else None
            metadata = json.loads(match.group(0)) if match else {}

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

                if value == "" or value == "None":
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

            print("[METADATA] Parsed metadata:", metadata)
            return metadata

        except Exception as e:
            print(f"[METADATA ERROR] Extraction Error: {e}")
            return {
                "name": name_match.group(1).strip() if name_match else "N/A",
                "age": "N/A",
                "gender": "N/A",
                "date_of_birth": "N/A",
                "patient_id": id_match.group(1).strip() if id_match else "N/A",
                "doctor_name": "N/A",
                "hospital_name": "N/A",
                "sample_type": "N/A",
            }
# Singleton instance
rag_service = RAGService()