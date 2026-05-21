import fitz  # PyMuPDF
import easyocr
import re
import os
from pathlib import Path

class OCRService:
    def __init__(self):
        # Industry Standard: Load the model once
        print("Initializing EasyOCR Engine...")
        self.reader = easyocr.Reader(['en'])

    def extract_text(self, file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        if ext == '.pdf':
            return self._extract_from_pdf(file_path)
        return self._extract_from_image(file_path)

    def _extract_from_pdf(self, path):
        text = ""
        with fitz.open(path) as doc:
            for page in doc:
                text += page.get_text()
        return self._clean_text(text)

    def _extract_from_image(self, path):
        # detail=0 gives a simple list of strings
        results = self.reader.readtext(str(path), detail=0)
        return self._clean_text(" ".join(results))

    def _clean_text(self, text):
        return re.sub(r'\s+', ' ', text).strip()

    def extract_medical_values(self, text: str):
        patterns = {
            'glucose': r'[Gg]lucose[:\s]+(\d+\.?\d*)',
            'bp': r'[Bb]lood\s?[Pp]ressure[:\s]+(\d+/\d+)',
            'bmi': r'[Bb][Mm][Ii][:\s]+(\d+\.?\d*)'
        }
        extracted = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                extracted[key] = match.group(1)
        return extracted

# Singleton instance
ocr_service = OCRService()
