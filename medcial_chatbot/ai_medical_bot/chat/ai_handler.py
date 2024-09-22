import google.generativeai as genai
import markdown2
import re
from datetime import timedelta

class AIHandler:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')

    def generate_response(self, user_input, patient):
        user_input_lower = user_input.lower()

        if "appointment" in user_input_lower and ("when" in user_input_lower or "date" in user_input_lower):
            return f"Your next appointment is on {patient.next_appointment.strftime('%B %d, %Y at %I:%M %p')}."

        reschedule_match = re.search(r"reschedule.*by (\d+) days", user_input_lower)
        if reschedule_match:
            days_to_reschedule = int(reschedule_match.group(1))
            new_appointment_date = patient.next_appointment + timedelta(days=days_to_reschedule)
            patient.next_appointment = new_appointment_date
            patient.save()  
            return f"Your appointment has been rescheduled to {new_appointment_date.strftime('%B %d, %Y at %I:%M %p')}."

        if "medical condition" in user_input_lower or "condition" in user_input_lower:
            return f"Here is information about your condition: {patient.medical_condition}"

        response = self.model.generate_content(user_input)
        response_html = markdown2.markdown(response.text)
        return response_html
