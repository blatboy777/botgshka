import os
import requests
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    if not data or 'message' not in data or 'text' not in data['message']:
        return "ok", 200
        
    chat_id = data['message']['chat']['id']
    text = data['message']['text']
    
    TOKEN = os.environ.get("TOKEN")
    GEMINI_KEY = os.environ.get("GEMINI_KEY")
    
    # Используем адрес модели через v1beta, это самый стандартный путь
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    try:
        resp = requests.post(url, json={"contents": [{"parts": [{"text": text}]}]})
        
        if resp.status_code == 200:
            result = resp.json()
            reply = result['candidates'][0]['content']['parts'][0]['text']
        else:
            reply = f"Ошибка Gemini: {resp.status_code}. Проверьте ключ API."
    except Exception as e:
        reply = f"Техническая ошибка: {str(e)}"
            
    # Отправка ответа в Telegram
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": chat_id, "text": reply})
            
    return "ok", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
