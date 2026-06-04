import base64
from groq import Groq
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.translation import get_language
from .models import ChatMessage

client = Groq(api_key=settings.GROQ_API_KEY)

LANG_PROMPTS = {
    'ru': 'Ты консультант аптеки DoriTJ в Таджикистане. Помогай подбирать лекарства по симптомам, предлагай аналоги. Отвечай на русском языке.',
    'tg': 'Ту мушовири дорухонаи DoriTJ дар Тоҷикистон. Дар интихоби доруҳо аз рӯи аломатҳо кӯмак кун, аналогҳо пешниҳод кун. Ба забони тоҷикӣ ҷавоб деҳ.',
    'en': 'You are a consultant at DoriTJ pharmacy in Tajikistan. Help choose medications based on symptoms, suggest analogues. Answer in English.',
}

@login_required
def consultant(request):
    history = ChatMessage.objects.filter(user=request.user).order_by('created_at')

    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        image = request.FILES.get('image')

        if not user_message and not image:
            return redirect('consultant')

        image_path = None
        if image:
            msg = ChatMessage.objects.create(
                user=request.user,
                role='user',
                message=user_message or '',
                image=image
            )
            image_path = msg.image.path
        else:
            msg = ChatMessage.objects.create(
                user=request.user,
                role='user',
                message=user_message or ''
            )

        try:
            lang = get_language() or 'ru'
            system_content = LANG_PROMPTS.get(lang, LANG_PROMPTS['ru'])

            if image_path:
                with open(image_path, 'rb') as f:
                    encoded = base64.b64encode(f.read()).decode('utf-8')
                ext = image.name.split('.')[-1].lower()
                mime = f'image/{ext}' if ext != 'jpg' else 'image/jpeg'
                data_uri = f'data:{mime};base64,{encoded}'

                content = [{'type': 'text', 'text': user_message or 'Опиши что на этом изображении'}]
                content.append({'type': 'image_url', 'image_url': {'url': data_uri}})

                response = client.chat.completions.create(
                    model='llama-3.2-90b-vision-preview',
                    messages=[
                        {'role': 'system', 'content': system_content},
                        {'role': 'user', 'content': content}
                    ]
                )
            else:
                response = client.chat.completions.create(
                    model='llama-3.3-70b-versatile',
                    messages=[
                        {'role': 'system', 'content': system_content},
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