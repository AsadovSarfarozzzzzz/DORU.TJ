from groq import Groq
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import ChatMessage

client = Groq(api_key=settings.GROQ_API_KEY)

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

        try:
            response = client.chat.completions.create(
                model='llama-3.3-70b-versatile',
                messages=[
                    {
                        'role': 'system',
                        'content': 'Ты консультант аптеки DoriTJ в Таджикистане. Помогай подбирать лекарства по симптомам, предлагай аналоги. Отвечай на русском любом языке в основе на таджитском.'
                    },
                    {'role': 'user', 'content': user_message}
                ]
            )
            ai_reply = response.choices[0].message.content

        except Exception as e:
            ai_reply = 'Извините, AI консультант временно недоступен.'
            print("ERROR:", e)

        ChatMessage.objects.create(
            user=request.user,
            role='assistant',
            message=ai_reply
        )
        return redirect('consultant')

    return render(request, 'chat.html', {'history': history})


@login_required
def clear_chat(request):
    ChatMessage.objects.filter(user=request.user).delete()
    return redirect('consultant')