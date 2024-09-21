import google.generativeai as genai
import markdown2

class AIHandler:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    def generate_response(self, user_input):
        response = self.model.generate_content(user_input)
        response_html = markdown2.markdown(response.text)
        return response_html