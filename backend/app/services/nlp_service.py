from transformers import pipeline

class NLPService:
    def __init__(self):
        # Industry Standard: Loading the 'Smart Doctor' model
        # This model knows: DISEASES, DRUGS, SYMPTOMS, etc.
        print("Loading Medical NLP Brain (Biomedical-NER)...")
        self.ner_pipeline = pipeline(
            "ner", 
            model="d4data/biomedical-ner-all", 
            aggregation_strategy="simple"
        )

    def extract_entities(self, text: str):
        """
        Reads the messy text and finds medical terms.
        """
        entities = self.ner_pipeline(text)
        
        # We group the findings so they look professional
        results = {
            "diseases": [],
            "medications": [],
            "symptoms": []
        }

        if not entities: return results # Safe check for empty results

        temp_entities = []

        for ent in entities:
            if ent['word'].startswith("##") and temp_entities:
                temp_entities[-1]['word'] += ent['word'].replace("##", "")
            else:
                temp_entities.append(ent)

        for ent in temp_entities:

            label = ent['entity_group']
            word = ent['word']
            if len(word) < 4: continue # Skip tiny fragments, industry practice

            if label == "Disease_disorder":
                results["diseases"].append(word)
            elif label == "Sign_symptom":
                results["symptoms"].append(word)
            elif label == "Medication":
                results["medications"].append(word)
            
        
        # Remove duplicates (Industry practice)
        for key in results:
            results[key] = list(set(results[key]))
            
        return results
    
    def _map_to_results(self, word, label, results):
        if len(word) < 3: return # Skip tiny fragments
        # Map the model's labels to our professional categories
        if label == "Disease_disorder":
            results["diseases"].append(word)
        elif label == "Sign_symptom":
            results["symptoms"].append(word)
        elif label == "Medication":
            results["medications"].append(word)

# Initialize the Singleton
nlp_service = NLPService()