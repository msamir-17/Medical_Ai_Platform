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
        
        for ent in entities:
            label = ent['entity_group']
            word = ent['word']
            
            # Map the model's labels to our professional categories
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

# Initialize the Singleton
nlp_service = NLPService()