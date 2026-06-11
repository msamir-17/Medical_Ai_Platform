class ReportClassifier:

    ALIASES = {
        "haemoglobin": "hemoglobin",
        "hb": "hemoglobin",
        "total_wbc_count": "wbc",
        "platelet_count": "platelets",
        "blood_glucose": "glucose",
        "serum_creatinine": "creatinine"
    }

    # 20 Categories - Full Medical Ontology
    CATEGORIES = {
        "Complete Blood Count (CBC)": ["haemoglobin", "wbc", "rbc", "platelets", "mcv", "mch", "mchc", "hematocrit", "rdw"],
        "Arterial Blood Gas (ABG)": ["pco2", "po2", "hco3", "base excess", "so2"],
        "Diabetes Profile": ["glucose", "hba1c", "fasting glucose", "post prandial glucose"],
        "Renal Function Test (KFT)": ["creatinine", "blood urea", "bun", "egfr", "uric acid"],
        "Liver Function Test (LFT)": ["alt", "ast", "sgpt", "sgot", "bilirubin", "alp", "albumin"],
        "Lipid Profile": ["cholesterol", "hdl", "ldl", "triglycerides", "vldl"],
        "Thyroid Profile": ["tsh", "t3", "t4"],
        "Urine Routine": ["urine ph", "protein", "ketones", "specific gravity", "leukocytes", "nitrite"],
        "Electrolyte Panel": ["sodium", "potassium", "chloride", "calcium", "magnesium"],
        "Iron Studies": ["ferritin", "iron", "tibc", "transferrin"],
        "Coagulation Profile": ["pt", "inr", "aptt"],
        "Cardiac Markers": ["troponin", "ck-mb", "myoglobin"],
        "Inflammatory Markers": ["crp", "esr", "il-6"],
        "Vitamin Panel": ["vitamin d", "vitamin b12", "folate"],
        "Fever Profile": ["dengue", "malaria", "typhoid", "widal", "ns1"],
        "Infectious Disease": ["hiv", "hbsag", "hcv", "syphilis"],
        "Hormone Panel": ["cortisol", "testosterone", "lh", "fsh", "prolactin"],
        "Pregnancy Panel": ["beta-hcg", "progesterone"],
        "Tumor Markers": ["psa", "cea", "ca-125", "afp"],
        "Biochemistry Report": ["amylase", "lipase", "ldh", "cpk"]
    }

    def _normalize_key(self, key: str) -> str:

        """Kachra saaf karke key ko standard banata hai."""
        # 1. Lowercase
        # 2. Spaces and dots hatao
        clean_key = key.lower().replace(".", "").replace(" ", "_")
        # 3. Alias check (e.g., 'hb' -> 'hemoglobin')
        return self.ALIASES.get(clean_key, clean_key)


    def classify_multi(self, found_markers: list) -> list:
        """Finds ALL matching report types in a single document."""
        detected_types = []
        normalized_found = [m.lower() for m in found_markers]

        for category, markers in self.CATEGORIES.items():
            # Agar kisi category ke 2 ya zyada markers milte hain, toh use add karo
            match_count = sum(1 for m in markers if any(m in fm for fm in normalized_found))
            
            if any(m in normalized_found for m in markers):
                detected_types.append(category)

        return detected_types if detected_types else ["General Lab Report"]

classifier = ReportClassifier()