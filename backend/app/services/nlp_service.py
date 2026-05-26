from transformers import pipeline
from rapidfuzz import process, utils
import re


class NLPService:
    # Industry Standard: A dictionary of correct medical terms
# In a giant project, we load this from a 1-million word file.
# For our project, we will use the most common terms.
    MEDICAL_VOCAB = [
        "nasopharyngeal", "carcinoma", "adenocarcinoma", "lymphadenopathy", 
        "hypertension", "diabetes", "metformin", "amlodipine", "asthma", 
        "biopsy", "histopathology", "malignant", "benign", "tumor", "tumour"
    ]

    def __init__(self):

        print("Loading Medical NLP Brain...")

        # Biomedical Named Entity Recognition Model
        self.ner_pipeline = pipeline(
            "ner",
            model="d4data/biomedical-ner-all",
            aggregation_strategy="simple"
        )

    def clean_entity_text(self, word: str) -> str:
        """
        Production-level entity cleaning
        """

        # Remove accidental tokenizer artifacts
        word = word.replace("##", "")

        # Fix spaces around hyphens
        # Example:
        # non - small cell  -> non-small cell
        word = re.sub(r"\s*-\s*", "-", word)

        # Remove extra spaces
        word = re.sub(r"\s+", " ", word)

        # Final cleanup
        word = word.strip()

        return word

    def map_entity_to_result(self, label, word, results):
        """
        Maps model labels into structured categories
        """

        if len(word) < 3:
            return

        if label == "Disease_disorder":
            results["diseases"].append(word)

        elif label == "Medication":
            results["medications"].append(word)

        elif label == "Sign_symptom":
            results["symptoms"].append(word)

    def remove_duplicates(self, items):
        """
        Removes duplicates while preserving order
        """

        return list(dict.fromkeys(items))

    def get_corrected_word(self, word: str):
        """
        Uses Fuzzy Matching to fix OCR/NER spelling errors.
        """
        if len(word) < 4: return word
        
        # extractOne finds the closest match from our MEDICAL_VOCAB
        # score_cutoff=80 means we only fix it if we are 80% sure
        match = process.extractOne(
            word, 
            self.MEDICAL_VOCAB, 
            processor=utils.default_process, 
            score_cutoff=80
        )
        
        if match:
            # match[0] is the string, match[1] is the score
            return match[0]
        return word

    def extract_entities(self, text: str):
        entities = self.ner_pipeline(text)
        results = {"diseases": [], "medications": [], "symptoms": []}
        if not entities: return results

        for ent in entities:
            try:
                word = ent["word"]
                label = ent["entity_group"]

                # 1. Professional Cleanup (Remove ## and spaces)
                clean_word = self.clean_entity_text(word)

                # 2. THE MAGIC STEP: Fuzzy Correction
                corrected_word = self.get_corrected_word(clean_word)

                # 3. Map to results
                self.map_entity_to_result(label, corrected_word, results)

            except Exception as e:
                print(f"Entity processing error: {e}")

        # Remove duplicates
        for key in results:
            results[key] = self.remove_duplicates(results[key])

        return results


# Singleton Instance
nlp_service = NLPService()