from django.shortcuts import render
from datetime import datetime
from .models import Patient, Conversation
from .ai_handler import AIHandler

def chat_view(request):
    
    patient = Patient.objects.first()
    if not patient:
        patient = Patient.objects.create(
            first_name="Jessy",
            last_name="Marry",
            date_of_birth="1999-10-08",
            phone_number="8870699909",
            email="jessy.mary@vit.edu",
            medical_condition="Hypertension",
            medication_regimen="Lisinopril",
            last_appointment="2024-09-10 09:00",
            next_appointment="2024-09-25 10:00",
            doctor_name="Dr. Chittibabu"
        )

    
    ai_handler = AIHandler(api_key="")

    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        bot_response = ai_handler.generate_response(user_input=user_input)

        
        Conversation.objects.create(patient=patient, message=user_input, response=bot_response)

    
    conversation_history = Conversation.objects.filter(patient=patient).order_by('-timestamp')

    return render(request, 'chat/chat.html', {
        'patient': patient,
        'conversation_history': conversation_history
    })
