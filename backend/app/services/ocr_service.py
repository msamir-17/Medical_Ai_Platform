import fitz
import easyocr
import re
from PIL import Image, ImageOps, ImageEnhance
import io

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
            "glucose": r"glucose[^0-9]+(\d+\.?\d*)",

            "hb": r"ha?emoglobin[^0-9]+(\d+\.?\d*)",

            "cholesterol": r"cholesterol[^0-9]+(\d+\.?\d*)",

            "creatinine": r"creatinine[^0-9]+(\d+\.?\d*)",

            

            "ph": r"ph[^0-9]+(\d+\.?\d*)",

            "pco2": r"pco2[^0-9]+(\d+\.?\d*)",

            "po2": r"po2[^0-9]+(\d+\.?\d*)",

            "bmi": r"bmi[^0-9]+(\d+\.?\d*)",

            "haemoglobin": r"[Hh]aemoglobin[:\s]+(\d+\.?\d*)",

            "wbc": r"Total\s?[Ww]\.?[Bb]\.?[Cc]\.?\s?Count[:\s]+(\d+)",

            "platelets": r"Platelet\s?Count[:\s]+(\d+)",
            
            "creatinine": r"Serum\s?Creatinine[:\s]+(\d+\.?\d*)"
        }

        extracted = {}

        for key, pattern in patterns.items():

            match = re.search(pattern, text, re.IGNORECASE) 

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
    
    def _enhance_image(self, img_bytes):
        """LAYER 1: Pixel Pre-processing. Standardizes contrast and removes color noise."""
        img = Image.open(io.BytesIO(img_bytes)).convert('L') # Convert to Grayscale
        img = ImageOps.autocontrast(img)
        img = ImageEnhance.Sharpness(img).enhance(2.0)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()

    def _reconstruct_layout(self, ocr_results):
        """LAYER 2 & 3: Clusters words into logical lines using Y-coordinate proximity."""
        # results format: [([box], text, confidence), ...]
        if not ocr_results: return ""

        # 1. Sort by Y-coordinate (Top to Bottom)
        ocr_results.sort(key=lambda x: x[0][0][1])

        lines = []
        if ocr_results:
            current_line = [ocr_results[0]]
            
            for i in range(1, len(ocr_results)):
                prev_y = current_line[-1][0][0][1]
                curr_y = ocr_results[i][0][0][1]
                
                # If vertical distance < 10 pixels, they are on the same line
                if abs(curr_y - prev_y) < 10:
                    current_line.append(ocr_results[i])
                else:
                    # Sort the finished line by X-coordinate (Left to Right)
                    current_line.sort(key=lambda x: x[0][0][0])
                    lines.append(current_line)
                    current_line = [ocr_results[i]]
            
            # Add the last line
            current_line.sort(key=lambda x: x[0][0][0])
            lines.append(current_line)

        # Convert to structured text representation
        structured_text = ""
        for line in lines:
            line_text = " | ".join([res[1] for res in line]) # Use '|' as column separator
            structured_text += line_text + "\n"
        
        return structured_text

    def extract_text(self, file_path: str):
        """The Main Entry Point: Coordinates the 7-Layer logic."""
        doc = fitz.open(file_path)
        full_structured_text = ""

        for page in doc:
            pix = page.get_pixmap(dpi=150)
            # Layer 1: Enhancement
            enhanced_img = self._enhance_image(pix.tobytes("png"))
            
            # Layer 2: Raw Extraction
            raw_results = self.reader.readtext(enhanced_img, detail=1)
            
            # Layer 3 & 4: Structural Reconstruction
            page_text = self._reconstruct_layout(raw_results)
            full_structured_text += page_text + "\n--- Page Break ---\n"

        doc.close()
        return full_structured_text

# Singleton Instance
ocr_service = OCRService()