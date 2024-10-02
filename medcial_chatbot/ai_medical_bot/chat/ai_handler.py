import openai
import google.generativeai as genai
import markdown2
import re
from datetime import timedelta
import langsmith
from langchain.prompts import PromptTemplate
from langsmith import traceable

class AIHandler:
    def __init__(self, api_key, model_choice='google'):
        self.api_key = api_key
        self.model_choice = model_choice
        
        if self.model_choice == 'google':
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        elif self.model_choice == 'openai':
            openai.api_key = self.api_key

    # @traceable(
    #     run_type="llm",
    #     name="AI_BOT_RESPONSE_GENERATOR",
    #     tags=["BOT_RESPONSE_GENERATOR"],
    #     metadata={"task":"token_check"}
    # )
    def generate_response(self, user_input, patient, conversation_summary):
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

        # Use conversation summary instead of full history for LLM call
        prompt_template = PromptTemplate(
            input_variables=["user_input", "doctor_name", "conversation_summary"],
            template="""
                    AI Role:
                    You are a health assistant designed to interact with patients regarding their health and care plan. Your primary goal is to respond to health-related inquiries, assist with treatment and medication-related requests, and facilitate communication between the patient and their doctor.

                    Task Objective:
                    Respond to patient inquiries about general health, lifestyle, medical conditions, medications, diet, and treatment plans.
                    Handle patient requests to reschedule appointments or modify treatment protocols by relaying them to the doctor.
                    Filter out unrelated, sensitive, or controversial topics to ensure only relevant health-related conversations are handled.

                    Task Input:
                    Patient message: A text input where the patient provides their query or request. This may include general health questions, details about their condition or medication, or requests for changes to appointments.
                    Doctor's Name: The name of the patient's doctor, to be used when relaying requests.

                    Task Instructions:
                    Health-related Queries:

                    If the patient asks a general health or lifestyle question, provide appropriate information.
                    If the patient asks about their medical condition, medication regimen, or diet, respond with advice or information relevant to their query.
                    Appointment or Treatment Requests:

                    If the patient requests an appointment modification (e.g., “Can we reschedule the appointment to next Friday at 3 PM?”), respond with:
                    “I will convey your request to Dr. [Doctor’s Name].”
                    Additionally, log a structured message that summarizes the request:
                    “Patient [Name] is requesting an appointment change from [current time] to [requested time].”
                    Topic Filtering:

                    Ignore or politely deflect unrelated, sensitive, or controversial topics. Ensure that the conversation stays within the bounds of health-related discussions.
                    Entity Extraction:


                    Task Output:
                    A relevant response to the patient's health-related query or request, formatted based on the task instructions only the text, nothing in bold or any other markdown format
                    For appointment or treatment modification requests, output a structured message confirming that the request will be relayed to the doctor.
                    Filter out irrelevant topics, ensuring the conversation remains focused on health-related matters.

                                    Conversation Summary:
                                    {conversation_summary}

                                    Patient message: "{user_input}"
                                    Doctor's Name: "{doctor_name}"
                                """
        )
        
        rendered_prompt = prompt_template.format(
            user_input=user_input,
            doctor_name=patient.doctor_name,
            conversation_summary=conversation_summary
        )
        if self.model_choice == 'google':
            response = self.model.generate_content(rendered_prompt)
            return response.text
        elif self.model_choice == 'openai':
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": rendered_prompt}
                ],
                max_tokens=150
            )
            return response.choices[0].message.content