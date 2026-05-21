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

        current_word = ""
        current_label = ""


        for ent in entities:

            label = ent['entity_group']
            word = ent['word']


            # If word starts with ##, it belongs to the previous word
            if word.startswith("##"):
                current_word += word.replace("##", "")
            else:
                if current_word: # Save the previous finished word
                    self._map_to_results(current_word, current_label, results)
                current_word = word
                current_label = label
        
        # Save the last word
        if current_word:
            self._map_to_results(current_word, current_label, results)

            
        
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