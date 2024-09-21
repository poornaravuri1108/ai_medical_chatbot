from django.shortcuts import render
from datetime import datetime
from .models import Patient

# Dummy AI response function
def ai_bot_response(user_input):
    if "appointment" in user_input.lower():
        return "I will convey your request to your doctor."
    return "Please provide more information about your health."

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