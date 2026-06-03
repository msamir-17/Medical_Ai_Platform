import fitz
import easyocr
import re


class OCRService:

    def __init__(self):

        print("Initializing High-Accuracy OCR Engine...")

        self.reader = easyocr.Reader(['en'])

    def extract_text(self, file_path: str):

        if file_path.lower().endswith('.pdf'):
            return self._extract_from_pdf_visually(file_path)

        return self._extract_from_image(file_path)

    # -----------------------------------------
    # PDF OCR
    # -----------------------------------------
    def _extract_from_pdf_visually(self, path):

        doc = fitz.open(path)

        full_text = ""

        for page_num, page in enumerate(doc):

            # Higher quality rendering
            pix = page.get_pixmap(dpi=300)
            # pix = page.get_pixmap(dpi=150)

            img_bytes = pix.tobytes("png")

            # Get OCR with confidence
            results = self.reader.readtext(
                img_bytes,
                detail=1
            )

            page_text = []

            for result in results:

                bbox, text, confidence = result

                # Filter garbage OCR
                if confidence > 0.45:
                    page_text.append(text)

            full_text += " ".join(page_text) + " "

        doc.close()

        return self._normalize_text(full_text)

    # -----------------------------------------
    # IMAGE OCR
    # -----------------------------------------
    def _extract_from_image(self, path):

        results = self.reader.readtext(
            path,
            detail=1
        )

        text_parts = []

        for result in results:

            bbox, text, confidence = result

            if confidence > 0.45:
                text_parts.append(text)

        text = " ".join(text_parts)

        return self._normalize_text(text)

    # -----------------------------------------
    # TEXT NORMALIZATION
    # -----------------------------------------
    def _normalize_text(self, text):

        # Remove extra spaces
        text = re.sub(r"\s+", " ", text)

        # Fix hyphen spacing
        text = re.sub(r"\s*-\s*", "-", text)

        # OCR repair dictionary
        repairs = {

            "nas haryn": "nasopharyngeal",
            "tum our": "tumor",
            "car cinoma": "carcinoma"

        }

        for broken, fixed in repairs.items():
            text = text.replace(broken, fixed)

        return text.strip()
    
    # -----------------------------------------
# MEDICAL VALUE EXTRACTION
# -----------------------------------------
    def extract_medical_values(self, text: str):


        patterns = {
            "glucose": r"[Gg]lucose[:\s]+(\d+\.?\d*)",

            "hb": r"[Hh]emoglobin[:\s]+(\d+\.?\d*)",

            "ph": r"[Pp][Hh][:\s]+(\d+\.?\d*)",

            "pco2": r"[Pp][Cc][Oo]2[:\s]+(\d+\.?\d*)",

            "po2": r"[Pp][Oo]2[:\s]+(\d+\.?\d*)",
            
            "bmi": r"[Bb][Mm][Ii][:\s]+(\d+\.?\d*)",

            "haemoglobin": r"[Hh]aemoglobin[:\s]+(\d+\.?\d*)",

            "wbc": r"Total\s?[Ww]\.?[Bb]\.?[Cc]\.?\s?Count[:\s]+(\d+)",

            "platelets": r"Platelet\s?Count[:\s]+(\d+)",
            
            "creatinine": r"Serum\s?Creatinine[:\s]+(\d+\.?\d*)"
        }

        extracted = {}

        for key, pattern in patterns.items():

            match = re.search(pattern, text)

            if match:
                extracted[key] = match.group(1)

        return extracted


    def interpret_markers(self, values: dict):
        """Provides human-readable meaning for lab markers."""
        # Industry Standard: Reference ranges (Common values)
        reference = {
            "haemoglobin": {"min": 13.5, "max": 17.5, "unit": "g/dL", "label": "Blood Level"},
            "wbc": {"min": 4000, "max": 11000, "unit": "/cmm", "label": "Immunity (WBC)"},
            "platelets": {"min": 150000, "max": 450000, "unit": "/cmm", "label": "Blood Clotting"},
            "glucose": {"min": 70, "max": 100, "unit": "mg/dL", "label": "Blood Sugar"},
            "cholesterol": {"min": 120, "max": 200, "unit": "mg/dL", "label": "Heart Fat"},
            "ph": {"min": 7.35, "max": 7.45, "unit": "", "label": "Blood Acidity (pH)"},
            "pco2": {"min": 35, "max": 45, "unit": "mmHg", "label": "Carbon Dioxide"},
            "po2": {"min": 80, "max": 100, "unit": "mmHg", "label": "Oxygen Level"}
        }

        interpreted = []
        for key, value in values.items():
            ref = reference.get(key)
            if ref:
                val_float = float(value)
                status = "Normal"
                color = "green"
                
                if val_float < ref["min"]:
                    status = "Low"
                    color = "blue"
                elif val_float > ref["max"]:
                    status = "High"
                    color = "red"

                interpreted.append({
                    "marker": key.upper(),
                    "value": value,
                    "unit": ref["unit"],
                    "meaning": ref["label"],
                    "status": status,
                    "color": color
                })
        return interpreted

# Singleton Instance
ocr_service = OCRService()