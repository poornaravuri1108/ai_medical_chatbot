from django.shortcuts import render
from datetime import datetime
from .models import Patient
import json
import getpass
import google.generativeai as genai
import markdown2

# Dummy AI response function
def ai_bot_response(user_input):
    GOOGLE_API_KEY = getpass.getpass("Enter api key: ")
    print(GOOGLE_API_KEY)
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')
    if "appointment" in user_input.lower():
        return "I will convey your request to your doctor."
    # return "Please provide more information about your health."
    response = model.generate_content(user_input)
    response_html = markdown2.markdown(response.text)
    return response_html

# Chat View
def chat_view(request):
    patient = Patient.objects.first()  # Assuming one patient for simplicity
    conversation_history = []

    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        bot_response = ai_bot_response(user_input)
        conversation_history.append({'user': user_input, 'bot': bot_response, 'timestamp': datetime.now()})

    return render(request, 'chat/chat.html', {
        'patient': patient,
        'conversation_history': conversation_history
    })