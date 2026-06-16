import fitz
import easyocr
import re
from PIL import Image, ImageOps, ImageEnhance
import io



class OCRService:

    def __init__(self):
        print("Initializing High-Accuracy OCR Engine...")
        self.reader = easyocr.Reader(['en'], gpu=False)
 
        self._last_pdf_path = None

    def extract_text(self, file_path: str) -> str:
        """
        Digital extraction first (with row grouping) → EasyOCR fallback.
        """
        self._last_pdf_path = file_path if file_path.lower().endswith(".pdf") else None
 
        doc = fitz.open(file_path)
        full_text = ""
 
        for page_num, page in enumerate(doc):
            words = page.get_text("words")  # (x0, y0, x1, y1, "text", block_no, line_no, word_no)
 
            if len(words) > 30:
                print(f"⚡ Page {page_num+1}: Using Structural Digital Extraction")
                
                # Filter empty values safely
                words = [w for w in words if str(w[4]).strip()]
                
                # Group words that share a similar vertical coordinate (Y axis)
                # We round Y coordinates to the nearest 4 pixels to account for baseline shifts.
                row_groups = {}
                for w in words:
                    y_coord = round(w[1] / 4) * 4
                    if y_coord not in row_groups:
                        row_groups[y_coord] = []
                    row_groups[y_coord].append(w)
                
                lines = []
                # Sort rows from top to bottom
                for y in sorted(row_groups.keys()):
                    # Sort words within the same row from left to right
                    row_words = sorted(row_groups[y], key=lambda w: w[0])
                    line_text = " ".join([w[4] for w in row_words])
                    lines.append(line_text)
                
                page_text = "\n".join(lines)
 
            else:
                print(f"📸 Page {page_num+1}: Low digital text. Running EasyOCR...")
                pix = page.get_pixmap(dpi=300)
                page_text = self._process_visual_layer(pix.tobytes("png"))
 
            full_text += page_text + "\n--- Page Break ---\n"
 
        doc.close()
        return full_text
    
    def _process_visual_layer(self, img_bytes):
        """
        FAST VISUAL LAYER: Processes images within a 10-second window 
        by using targeted structural configurations.
        """
        enhanced_img = self._enhance_image(img_bytes)
        
        # Speed Optimization: Set optimal batch sizes and restrict thresholds 
        # to prevent EasyOCR from spending time scanning empty white backgrounds.
        raw_results = self.reader.readtext(
            enhanced_img, 
            detail=1, 
            batch_size=16,      # Increased batch size for faster processing
            width_ths=0.5,      # Lower merge window reduces processing loops
            add_margin=0.1,
            slope_ths=0.1,      # Prevents scanning skewed lines
            ycenter_ths=0.5
        )
        
        return self._reconstruct_layout(raw_results)

    # -----------------------------------------
    # PDF OCR
    # -----------------------------------------
    def _extract_from_pdf_visually(self, path):
        doc = fitz.open(path)
        full_text = ""

        for page_num, page in enumerate(doc):
            # Speed Optimization: Use 200 DPI instead of 300 DPI.
            # This balances processing speed with text clarity.
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes("png")

            results = self.reader.readtext(img_bytes, detail=1, batch_size=16)
            
            page_text_elements = []
            for result in results:
                bbox, text, confidence = result
                # Fast numeric rescue rule
                if confidence > 0.40 or (any(char.isdigit() for char in text) and confidence > 0.22):
                    page_text_elements.append(text)

            full_text += " ".join(page_text_elements) + "\n"

        doc.close()
        return self._normalize_text(full_text)
    # -----------------------------------------
    # IMAGE OCR
    # -----------------------------------------
    def _extract_from_image(self, path):
        # Open and adaptively resize the image if it is too large, saving processing time
        img = Image.open(path)
        if max(img.size) > 2000:
            img.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
            
        results = self.reader.readtext(img, detail=1, batch_size=16)
        text_parts = []

        for result in results:
            bbox, text, confidence = result
            if confidence > 0.40 or (any(char.isdigit() for char in text) and confidence > 0.22):
                text_parts.append(text)

        text = " ".join(text_parts)
        return self._normalize_text(text)

    # -----------------------------------------
    # TEXT NORMALIZATION
    # -----------------------------------------
    def _normalize_text(self, text):

        # Remove extra spaces
        # collapse multiple blank lines
        text = re.sub(r"\n{2,}", "\n", text)

        # remove repeated spaces
        text = re.sub(r"[ \t]+", " ", text)

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
    def extract_medical_values(self, text: str) -> dict:
        """
        Hybrid Extraction Strategy

        Layer 1:
            Coordinate-aware extraction from digital PDFs.

        Layer 2:
            Regex-based extraction from reconstructed text.

        Final:
            Merge both, giving priority to coordinate extraction.
        """

        coord_results = {}
        regex_results = {}

        # -----------------------------
        # Layer 1 : Coordinate parser
        # -----------------------------
        if getattr(self, "_last_pdf_path", None):
            try:
                print("🎯 Layer 1: Coordinate Extraction")

                high_fidelity_lines = self._get_high_fidelity_lines(
                    self._last_pdf_path
                )

                coord_results = self._parse_lines_smart(
                    high_fidelity_lines
                )

                print("COORD RESULTS:", coord_results)

            except Exception as e:
                print(f"⚠️ Coordinate parser failed: {e}")

        # -----------------------------
        # Layer 2 : Regex parser
        # -----------------------------
        print("📄 Layer 2: Regex Extraction")

        regex_results = self._parse_lines_smart(
            text.splitlines()
        )
        print("REGEX RESULTS:", regex_results)
        # -----------------------------
        # Merge
        # Coordinate results override regex
        # -----------------------------
        final_results = regex_results.copy()
        final_results.update(coord_results)

        print(f"✅ Final extracted markers: {final_results}")

        return final_results
    
    def interpret_markers(self, values: dict) -> list:

        reference_ranges = {
            "glucose": (70, 100, "mg/dL"),
            "hba1c": (4.0, 5.6, "%"),
            "cholesterol": (0, 200, "mg/dL"),
            "triglycerides": (0, 150, "mg/dL"),
            "haemoglobin": (12, 17, "g/dL"),
            "wbc": (4000, 11000, "/cmm"),
            "platelets": (150000, 450000, "/cmm"),
            "creatinine": (0.5, 1.5, "mg/dL"),
            "uric acid": (3.4, 7.0, "mg/dL"),
            "crp": (0, 6, "mg/L"),
            "esr": (0, 20, "mm/hr"),
            "tsh": (0.4, 4.5, "uIU/mL"),
        }

        interpreted = []

        for marker, value in values.items():

            if marker not in reference_ranges:
                continue

            try:
                value = float(value)

                low, high, unit = reference_ranges[marker]

                if value < low:
                    status = "Low"
                    color = "blue"
                elif value > high:
                    status = "High"
                    color = "red"
                else:
                    status = "Normal"
                    color = "green"

                interpreted.append({
                    "marker": marker.upper(),
                    "value": value,
                    "unit": unit,
                    "status": status,
                    "color": color,
                    "ref_range": f"{low} - {high}",
                })

            except Exception:
                pass

        return interpreted
    
    def _enhance_image(self, img_bytes):
        """FAST PIXEL ENHANCEMENT: Runs in milliseconds using light PIL operations."""
        img = Image.open(io.BytesIO(img_bytes))
        img = ImageOps.grayscale(img)
        
        # Increase contrast slightly to sharpen numeric values without generating noise
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5) 
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

    def _reconstruct_layout(self, ocr_results):
        """
        Reconstruct text while preserving rows and approximate columns.
        """
        if not ocr_results:
            return ""

        # Sort top -> bottom
        ocr_results.sort(key=lambda x: x[0][0][1])

        lines = []
        current_line = [ocr_results[0]]

        for item in ocr_results[1:]:
            prev_y = current_line[-1][0][0][1]
            curr_y = item[0][0][1]

            # Same visual row
            if abs(curr_y - prev_y) < 8:
                current_line.append(item)
            else:
                current_line.sort(key=lambda x: x[0][0][0])
                lines.append(current_line)
                current_line = [item]

        current_line.sort(key=lambda x: x[0][0][0])
        lines.append(current_line)

        reconstructed = []

        for line in lines:
            text = ""
            prev_end = 0

            for box, word, conf in line:
                x_start = box[0][0]
                x_end = box[1][0]

                # spacing based on x distance
                gap = max(1, int((x_start - prev_end) / 12))

                text += (" " * gap) + word

                prev_end = x_end

            reconstructed.append(text.rstrip())

        return "\n".join(reconstructed)

    def _parse_lines_smart(self, lines: list[str]) -> dict:
        """
        Smart parser that extracts RESULT values while avoiding
        reference ranges whenever possible.
        """
        print("=" * 80)
        print("DEBUG: Total lines =", len(lines))
        for i, line in enumerate(lines[:30]):
            print(f"{i}: {repr(line)}")

        print("=" * 80)

        extracted = {}

        field_patterns = {
            "glucose": r"\bglucose\b",
            "hba1c": r"\bhb\s*a1c\b",
            "cholesterol": r"\bcholesterol\b",
            "triglycerides": r"\btriglycerides\b",
            "haemoglobin": r"\bha?emoglobin\b",
            "wbc": r"\b(total\s*w\.?b\.?c|w\.?b\.?c)\b",
            "platelets": r"\bplatelet",
            "creatinine": r"\bcreatinine\b",
            "uric_acid": r"\buric\s*acid\b",
            "ph": r"\bph\b",
            "pco2": r"\bpco2\b",
            "po2": r"\bpo2\b",
            "crp": r"\bcrp\b|\bc-?reactive protein\b",
            "esr": r"\besr\b",
            "tsh": r"\btsh\b",
        }

        for raw_line in lines:
            

            line = re.sub(r"\s+", " ", raw_line).strip()

            if not line:
                continue

            lower_line = line.lower()

            for key, pattern in field_patterns.items():

                if key in extracted:
                    continue
                print(f"LINE: {line}")
                print(f"LOWER: {lower_line}")

                if not re.search(pattern, lower_line):
                    continue

                all_numbers = re.findall(
                    r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?(?![A-Za-z])",
                    line
                )

                if not all_numbers:
                    continue

                candidate = None

                # -------------------------
                # pH special handling
                # -------------------------
                if key == "ph":

                    decimals = [
                        n for n in all_numbers
                        if "." in n
                    ]

                    if decimals:
                        candidate = decimals[0]
                    print("NUMBERS:", all_numbers)

                else:

                    # Detect reference range
                    range_match = re.search(
                        r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)",
                        line
                    )

                    if range_match:

                        low, high = range_match.groups()

                        for num in all_numbers:
                            if num != low and num != high:
                                candidate = num
                                break

                    # fallback
                    if candidate is None:
                        candidate = all_numbers[0]
                        print("NUMBERS:", all_numbers)

                if candidate is not None:
                    extracted[key] = candidate
                    print(f"✅ MATCHED FIELD: {key}")
                    print(f"📄 LINE: {line}")
                    print(f"🔢 NUMBERS FOUND: {all_numbers}")
                    print(f"🎯 CANDIDATE: {candidate}")
                    print(f"🔥 STORED: {key} -> {candidate}")
                    print(f"🔥 STORED: {key} -> {candidate}")

        return extracted

    def _get_high_fidelity_lines(self, file_path: str):
        """
        LAYER 1: Uses PyMuPDF coordinates to group words into 
        perfectly aligned rows (Left-to-Right).
        """
        import fitz
        doc = fitz.open(file_path)
        structured_lines = []

        for page in doc:
            # Get words: (x0, y0, x1, y1, "word", block_no, line_no, word_no)
            words = page.get_text("words")

            print("\n===== RAW WORDS =====")
            for w in words[:20]:
                print(w)
            print("=====================\n")
            
            # Group words by their Block and Line number
            rows = {}

            for w in words:
                block_no = w[5]
                line_no = w[6]

                key = (block_no, line_no)
                rows.setdefault(key, []).append(w)

            structured_lines = []

            for key in sorted(rows.keys):
                row = sorted(rows[key], key=lambda x: x[0])  # x coordinate
                structured_lines.append(
                    " ".join(word[4] for word in row)
                )

        
        doc.close()
        print("\n===== HIGH FIDELITY LINES =====")
        for line in structured_lines[:30]:
            print(repr(line))
        print("================================\n")

        
        return structured_lines

# Singleton Instance
ocr_service = OCRService()