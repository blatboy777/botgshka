import os
import requests
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return "Бот работает!", 200
        
    data = request.json
    if not data or 'message' not in data:
        return "ok", 200
        
    chat_id = data['message']['chat']['id']
    text = data['message'].get('text', '...')
    
    TOKEN = os.environ.get("TOKEN")
    GEMINI_KEY = os.environ.get("GEMINI_KEY")
    
    # Жесткий список моделей: бот будет пробовать их по очереди, пока не пробьет блокировку
    models_to_try = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-1.0-pro",
        "gemini-pro"
    ]
    
    reply = None
    error_log = ""
    
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
        try:
            resp = requests.post(url, json={"contents": [{"parts": [{"text": text}]}]})
            if resp.status_code == 200:
                # Успех! Забираем текст и немедленно выходим из цикла
                reply = resp.json()['candidates'][0]['content']['parts'][0]['text']
                break
            else:
                # Записываем ошибку, чтобы понимать, кто отказал, и идем к следующей модели
                msg = resp.json().get('error', {}).get('message', 'Ошибка')
                error_log += f"\n[{model}: {msg}]"
        except Exception as e:
            error_log += f"\n[{model}: {str(e)}]"
            
    # Если вообще ни одна модель не пустила (что маловероятно)
    if not reply:
        reply = f"Ни одна модель не ответила. Лог ошибок от Google: {error_log}"
            
    # Отправка финального ответа в Telegram
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": chat_id, "text": reply})
            
    return "ok", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
