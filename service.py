import google.generativeai as genai
from dotenv import load_dotenv
import os
import pandas as pd
import re

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class ChatbotService:
    def __init__(self):
        self.model = genai.GenerativeModel(os.getenv("MODEL_VERSIE", "gemini-pro"))
        self.tracking_data = self.load_tracking_data()
        
    def load_tracking_data(self):
        """Laad de tracking codes uit CSV"""
        try:
            df = pd.read_csv('tracking_codes.csv', sep='\t')
            return df
        except:
            # Als CSV niet bestaat, maak een lege DataFrame
            return pd.DataFrame()
    
    def extract_tracking_code(self, prompt):
        """Extraheer tracking code uit de vraag van de gebruiker"""
        # Zoek naar codes zoals 3SAB123456789NL, 9876543210, etc.
        patterns = [
            r'\b[A-Z0-9]{10,20}\b',  # Algemene codes
            r'\b\d{10,15}\b',        # Alleen cijfers
            r'\b[A-Z]{2,3}\d{8,15}[A-Z]{2}\b'  # PostNL format
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, prompt.upper())
            if matches:
                return matches[0]
        return None
    
    def get_tracking_info(self, code):
        """Zoek tracking informatie op basis van code"""
        if self.tracking_data.empty:
            return None
        
        # Zoek de code (case insensitive)
        code_upper = str(code).upper()
        result = self.tracking_data[
            self.tracking_data['TrackTraceCode'].astype(str).str.upper() == code_upper
        ]
        
        if not result.empty:
            pakket = result.iloc[0]
            return {
                'code': pakket['TrackTraceCode'],
                'vervoerder': pakket['Vervoerder'],
                'verwacht': pakket['VerwachtAankomsttijdstip'],
                'status': pakket['Status'],
                'opmerking': pakket['Opmerking'] if pd.notna(pakket['Opmerking']) else 'Geen opmerking'
            }
        return None
    
    def get_antwoord(self, prompt):
        """Hoofdfunctie: bepaal of het een tracking vraag is of een algemene vraag"""
        
        # 1. Check of het een tracking vraag is
        tracking_code = self.extract_tracking_code(prompt)
        
        if tracking_code:
            tracking_info = self.get_tracking_info(tracking_code)
            
            if tracking_info:
                # Formatteer tracking response
                response = f"""
📦 **PAKKET GEVONDEN - {tracking_info['code']}**

🚚 **Vervoerder:** {tracking_info['vervoerder']}
📅 **Verwacht:** {tracking_info['verwacht']}
✅ **Status:** {tracking_info['status']}
📝 **Opmerking:** {tracking_info['opmerking']}

*Voor meer informatie, bezoek de website van {tracking_info['vervoerder']}*
                """
                return response
            else:
                return f"❌ Ik kan geen informatie vinden over tracking code: {tracking_code}. Controleer of de code correct is."
        
        # 2. Als het geen tracking vraag is, gebruik AI voor antwoord
        # Voeg context toe voor de AI over wat deze chatbot doet
        context = """
Je bent Billie, de klantenservice chatbot van een e-commerce bedrijf.
Je kunt helpen met:
1. Pakket tracking - vraag om een Track & Trace code
2. Retourneren - voorwaarden en procedures
3. Betalingen - methoden en problemen
4. Algemene vragen over bestellingen

Wees vriendelijk, behulpzaam en bondig in je antwoorden.
Als je iets niet weet, adviseer dan contact op te nemen via de klantenservice telefoon.
        """
        
        full_prompt = f"{context}\n\nGebruikersvraag: {prompt}"
        
        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Sorry, er ging iets mis: {str(e)}"

# Voor backward compatibility
def get_antwoord(prompt):
    service = ChatbotService()
    return service.get_antwoord(prompt)
