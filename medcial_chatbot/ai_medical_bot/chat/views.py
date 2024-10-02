from django.shortcuts import render
from langchain.memory import ConversationSummaryMemory, ChatMessageHistory
from langchain_openai import OpenAI
from django.conf import settings
from datetime import timedelta
from .models import Patient, Conversation
from .ai_handler import AIHandler

def opening_view(request):
    return render(request, 'chat.html')

def chat_view(request):
    # Fetch or create the patient
    patient = Patient.objects.first()
    if not patient:
        patient = Patient.objects.create(
            first_name="Jessy",
            last_name="Mary",
            date_of_birth="1999-10-08",
            phone_number="8870699909",
            email="jessy.mary@vit.edu",
            medical_condition="Hypertension. The patient is on Lisinopril for blood pressure management.",
            medication_regimen="Lisinopril",
            last_appointment="2024-09-10 09:00",
            next_appointment="2024-09-25 10:00",
            doctor_name="Dr. Chittibabu"
        )

    selected_model = request.POST.get('model', 'google')
    api_key = settings.OPENAI_API_KEY if selected_model == 'openai' else settings.GEMINI_API_KEY

    ai_handler = AIHandler(api_key=api_key, model_choice=selected_model)

    history = ChatMessageHistory()
    if patient.conversation_summary:

        memory = ConversationSummaryMemory(llm=OpenAI(temperature=0), buffer=patient.conversation_summary, chat_memory=history, return_messages=True)
    else:
        memory = ConversationSummaryMemory(llm=OpenAI(temperature=0), chat_memory=history, return_messages=True)

    if request.method == 'POST':
        user_input = request.POST.get('user_input')

        conversation_history = Conversation.objects.filter(patient=patient).order_by('timestamp').values('message', 'response')
        for conv in conversation_history:
            history.add_user_message(conv['message'])
            history.add_ai_message(conv['response'])

        bot_response = ai_handler.generate_response(user_input=user_input, patient=patient, conversation_summary=memory.buffer)

        Conversation.objects.create(patient=patient, message=user_input, response=bot_response)

        messages = memory.chat_memory.messages
        new_summary = memory.predict_new_summary(messages, patient.conversation_summary)
        patient.conversation_summary = new_summary
        patient.save()

    conversation_history = Conversation.objects.filter(patient=patient).order_by('timestamp')

    return render(request, 'chat/chat.html', {
        'patient': patient,
        'conversation_history': conversation_history
    })
