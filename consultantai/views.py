import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import ChatMessage

@login_required
def consultant(request):
    history = ChatMessage.objects.filter(user=request.user).order_by('created_at')

    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        if not user_message:
            return redirect('consultant')

        ChatMessage.objects.create(
            user=request.user,
            role='user',
            message=user_message
        )

        messages_history = [
            {'role': msg.role, 'content': msg.message}
            for msg in history
        ]
        messages_history.append({'role': 'user', 'content': user_message})

        try:
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'x-api-key': settings.CLAUDE_API_KEY,
                    'anthropic-version': '2023-06-01',
                    'content-type': 'application/json',
                },
                json={
                    'model': 'claude-sonnet-4-20250514',
                    'max_tokens': 1024,
                    'system': '''Ты AI консультант аптеки DoriTJ в Таджикистане.
Помогаешь подобрать лекарства по симптомам, объясняешь инструкции,
предлагаешь аналоги. Советуй обращаться к врачу в серьёзных случаях.
Отвечай на русском языке.''',
                    'messages': messages_history
                }
            )
            ai_reply = response.json()['content'][0]['text']
        except Exception as e:
            ai_reply = 'Извините, AI консультант временно недоступен.'
            print(e)

        ChatMessage.objects.create(
            user=request.user,
            role='assistant',
            message=ai_reply
        )
        return redirect('consultant')

    return render(request, 'consultant/chat.html', {'history': history})


@login_required
def clear_chat(request):
    ChatMessage.objects.filter(user=request.user).delete()
    return redirect('consultant')