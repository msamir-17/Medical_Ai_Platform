import fitz
import easyocr
import re
from PIL import Image, ImageOps, ImageEnhance
import io

class OCRService:

    def __init__(self):

        print("Initializing High-Accuracy OCR Engine...")

        self.reader = easyocr.Reader(['en'],gpu=False )

    def extract_text(self, file_path: str):
        """
        Digital extraction first (with block sorting) -> EasyOCR fallback.
        """
        doc = fitz.open(file_path)
        full_text = ""

        for page_num, page in enumerate(doc):
            # 1. Try Digital Extraction with Structural Sorting
            words = page.get_text("words") # (x0, y0, x1, y1, word, block_no, line_no, word_no)
            
            # Agar meaningful text hai (>200 chars)
            if len(words) > 50:
                print(f"⚡ Page {page_num+1}: Using Structural Digital Extraction")
                # Sort by Block No, then Line No, then X-coordinate
                words.sort(key=lambda w: (w[5], w[6], w[0]))
                
                lines = []
                if words:
                    cur_block, cur_line = words[0][5], words[0][6]
                    cur_line_words = []
                    for w in words:
                        if w[5] == cur_block and w[6] == cur_line:
                            cur_line_words.append(w[4])
                        else:
                            lines.append(" ".join(cur_line_words))
                            cur_line_words = [w[4]]
                            cur_block, cur_line = w[5], w[6]
                    lines.append(" ".join(cur_line_words))
                page_text = "\n".join(lines)
            
            else:
                # 2. Fallback to Vision OCR for Scanned Pages
                print(f"📸 Page {page_num+1}: Low digital text. Running EasyOCR...")
                pix = page.get_pixmap(dpi=150)
                page_text = self._process_visual_layer(pix.tobytes("png"))
            
            full_text += page_text + "\n--- Page Break ---\n"

        doc.close()
        return full_text
    def _process_visual_layer(self, img_bytes):
        """
        REUSABLE COMPONENT: Runs Enhancement -> Raw OCR -> Layout Reconstruction
        This ensures both Images and PDFs get the same HIGH accuracy.
        """
        # 1. Layer 1: Image Enhancement (Contrast/Sharpness)
        enhanced_img = self._enhance_image(img_bytes)
        
        # 2. Layer 2: Raw Coordinate Extraction
        raw_results = self.reader.readtext(enhanced_img, detail=1, batch_size=4)
        
        # 3. Layer 3 & 4: Structural Reconstruction
        return self._reconstruct_layout(raw_results)

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
            results = self.reader.readtext(img_bytes, detail=1)
            page_text = self._reconstruct_layout(results)
            full_text += page_text + "\n"

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
        """
        Extract medical values line-by-line instead of searching
        the entire document. This greatly reduces wrong matches.
        """

        extracted = {}

        # Normalize lines
        lines = [
            re.sub(r"\s+", " ", line).strip()
            for line in text.splitlines()
            if line.strip()
        ]

        field_patterns = {
            "glucose": r"\bglucose\b",
            "hba1c": r"\bhb\s*a1c\b",
            "cholesterol": r"\bcholesterol\b",
            "triglycerides": r"\btriglycerides\b",
            "haemoglobin": r"\bha?emoglobin\b",
            "wbc": r"\bw\.?b\.?c\b|\btotal white\b",
            "platelets": r"\bplatelet",
            "creatinine": r"\bcreatinine\b",
            "uric acid": r"\buric\s+acid\b",
            "ph": r"\bph\b",
            "pco2": r"\bpco2\b",
            "po2": r"\bpo2\b",
            "crp": r"\bc-?reactive protein\b|\bcrp\b",
            "esr": r"\besr\b",
            "tsh": r"\btsh\b",
        }

        for line in lines:
            lower_line = line.lower()

            for key, pattern in field_patterns.items():

                if key in extracted:
                    continue

                if re.search(pattern, lower_line, re.IGNORECASE):

                    numbers = re.findall(r"\d+(?:\.\d+)?", line)

                    if not numbers:
                        continue

                    # pH should prefer decimal values like 7.279
                    if key == "ph":
                        decimal_values = [n for n in numbers if "." in n]
                        if decimal_values:
                            extracted[key] = decimal_values[0]
                        continue

                    # For all other tests, use the first number on the same line
                    extracted[key] = numbers[0]

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



# Singleton Instance
ocr_service = OCRService()