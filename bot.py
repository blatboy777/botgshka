import os
import requests
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    print(f"Пришли данные: {data}")
    
    if 'message' in data and 'text' in data['message']:
        chat_id = data['message']['chat']['id']
        text = data['message']['text']
        
        TOKEN = os.environ.get("TOKEN")
        GEMINI_KEY = os.environ.get("GEMINI_KEY")
        
        # Запрос к Gemini (используем стабильную версию)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_KEY}"
        resp = requests.post(url, json={"contents": [{"parts": [{"text": text}]}]})
        
        if resp.status_code == 200:
            try:
                reply = resp.json()['candidates'][0]['content']['parts'][0]['text']
            except:
                reply = "Ошибка обработки ответа от ИИ."
        else:
            reply = f"Ошибка Gemini: {resp.status_code}"
            
        # Отправка ответа в Telegram
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      json={"chat_id": chat_id, "text": reply})
            
    return "ok", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
