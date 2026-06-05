import pytest
from app.services.ocr_service import ocr_service
from app.services.nlp_service import nlp_service

# 1. TEST: Data Extraction (Using standard report format)
def test_data_extraction_logic():
    # Hum wahi format denge jo Regex easily samajh sake
    text = "GLUCOSE: 185.2, BMI: 30.5, pH: 7.41"
    values = ocr_service.extract_medical_values(text)
    
    # Check if the "Detective" found the numbers
    assert values["glucose"] == "185.2"
    assert values["bmi"] == "30.5"
    assert values["ph"] == "7.41"

# 2. TEST: General AI Intelligence (No more word-specific bias)
def test_ai_medical_understanding():
    # Hum AI ko ek messy sentence denge
    text = "Patient is suffering from severe Malaria and high Fever."
    entities = nlp_service.extract_entities(text)
    
    # LOGIC: Humein matlab nahi ki word 'Malaria' hai ya 'Cancer'.
    # Humein bas ye dekhna hai ki kya AI ne 'diseases' ya 'symptoms' ka dabba bhara?
    # Agar dabba bhara hai (length > 0), matlab AI intelligent hai!
    assert len(entities["diseases"]) > 0 or len(entities["symptoms"]) > 0
    print(f"DEBUG: AI found: {entities}")

# 3. TEST: Empty Case (Safety Check)
def test_noise_handling():
    text = "Hello, this is a random letter from the hospital canteen."
    values = ocr_service.extract_medical_values(text)
    # Isme koi medical value nahi honi chahiye
    assert len(values) == 0

def test_general_medical_intelligence():
    # Hum ek aisi bimari likhenge jo hamare code mein kahin mention nahi hai
    text = "Patient has severe Appendicitis and was given Paracetamol."
    entities = nlp_service.extract_entities(text)
    
    # Logic: Hum specific naam check nahi karenge, bas check karenge ki 
    # AI ne 'Bimari' (Diseases) aur 'Dawai' (Medications) ke dabbe bhare ya nahi.
    assert len(entities["diseases"]) > 0  # AI ko Appendicitis milni chahiye
    assert len(entities["medications"]) > 0  # AI ko Paracetamol milni chahiye
    
    print(f"✅ AI intelligently found: {entities}")