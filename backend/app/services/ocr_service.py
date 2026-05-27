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

            "bp": r"[Bb]lood\s?[Pp]ressure[:\s]+(\d+/\d+)",

            "bmi": r"[Bb][Mm][Ii][:\s]+(\d+\.?\d*)",

            "hemoglobin": r"[Hh]emoglobin[:\s]+(\d+\.?\d*)",

            "wbc": r"[Ww][Bb][Cc][:\s]+(\d+)",

        }

        extracted = {}

        for key, pattern in patterns.items():

            match = re.search(pattern, text)

            if match:
                extracted[key] = match.group(1)

        return extracted




# Singleton Instance
ocr_service = OCRService()