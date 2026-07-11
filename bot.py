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
    
    # Список адресов: сначала пробуем стабильный v1 со свежим именем, потом v1beta
    urls = [
        f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_KEY}",
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_KEY}"
    ]
    
    reply = None
    last_error = ""
    
    for url in urls:
        try:
            resp = requests.post(url, json={"contents": [{"parts": [{"text": text}]}]})
            if resp.status_code == 200:
                reply = resp.json()['candidates'][0]['content']['parts'][0]['text']
                break
            else:
                try:
                    last_error = resp.json().get('error', {}).get('message', f"Код {resp.status_code}")
                except:
                    last_error = f"Статус {resp.status_code}"
        except Exception as e:
            last_error = str(e)
            
    if not reply:
        reply = f"Ошибка авторизации или модели Gemini. Ответ Google: {last_error}"
            
    # Отправка ответа в Telegram
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": chat_id, "text": reply})
            
    return "ok", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
