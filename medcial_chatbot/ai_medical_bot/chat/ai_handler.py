import google.generativeai as genai
import markdown2
import re
from datetime import timedelta
import langsmith
from langchain.prompts import PromptTemplate
from langsmith import traceable

class AIHandler:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.client = None

    def initialize_tracing(self, endpoint, project, langsmith_api_key):
        self.client = langsmith.Client(api_key=langsmith_api_key, web_url=endpoint)
        self.project = project

    @traceable(
        run_type="llm",
        name="AI_BOT_RESPONSE_GENERATOR",
        tags=["BOT_RESPONSE_GENERATOR"],
        metadata={"task":"token_check"}
    )
    def generate_response(self, user_input, patient):
        user_input_lower = user_input.lower()

        responses = []

        if "appointment" in user_input_lower and ("when" in user_input_lower or "date" in user_input_lower):
            responses.append(f"Your next appointment is on {patient.next_appointment.strftime('%B %d, %Y at %I:%M %p')}.")

        reschedule_match = re.search(r"reschedule.*by (\d+) days", user_input_lower)
        if reschedule_match:
            days_to_reschedule = int(reschedule_match.group(1))
            new_appointment_date = patient.next_appointment + timedelta(days=days_to_reschedule)
            patient.next_appointment = new_appointment_date
            patient.save()  
            responses.append(f"Your appointment has been rescheduled to {new_appointment_date.strftime('%B %d, %Y at %I:%M %p')}.")

        if "medical condition" in user_input_lower or "condition" in user_input_lower:
            responses.append(f"Here is information about your condition: {patient.medical_condition}")

        if responses:
            return " ".join(responses)
        
        prompt_template = PromptTemplate(
            input_variables=["user_input", "doctor_name"],
            template="""
                AI Role:
                You are a health assistant designed to interact with patients regarding their health and care plan. Your primary goal is to respond to health-related inquiries, assist with treatment and medication-related requests, and facilitate communication between the patient and their doctor.

                Task Objective:
                Respond to patient inquiries about general health, lifestyle, medical conditions, medications, diet, and treatment plans.
                Handle patient requests to reschedule appointments or modify treatment protocols by relaying them to the doctor.
                Filter out unrelated, sensitive, or controversial topics to ensure only relevant health-related conversations are handled.
                
                Task Input:
                Patient message: "{user_input}"
                Doctor's Name: "{doctor_name}"

                Task Instructions:
                Health-related Queries:
                - If the patient asks a general health or lifestyle question, provide appropriate information.
                - If the patient asks about their medical condition, medication regimen, or diet, respond with advice or information relevant to their query.
                
                Appointment or Treatment Requests:
                - If the patient requests an appointment modification (e.g., “Can we reschedule the appointment to next Friday at 3 PM?”), respond with:
                “I will convey your request to Dr. {doctor_name}.”
                - Log a structured message summarizing the request.

                Topic Filtering:
                - Ignore or politely deflect unrelated, sensitive, or controversial topics.
            """
        )
        
        rendered_prompt = prompt_template.format(
            user_input=user_input,
            doctor_name=patient.doctor_name
        )

        response = self.model.generate_content(rendered_prompt)

        response_html = markdown2.markdown(response.text)
        return response_html
        
