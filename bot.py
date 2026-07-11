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
    
    # Используем версию v1 и самую стабильную модель gemini-1.0-pro
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.0-pro:generateContent?key={GEMINI_KEY}"
    
    payload = {"contents": [{"parts": [{"text": text}]}]}
    
    try:
        response = requests.post(url, json=payload)
        res_data = response.json()
        
        if response.status_code == 200:
            reply = res_data['candidates'][0]['content']['parts'][0]['text']
        else:
            reply = f"Ошибка {response.status_code}: {res_data.get('error', {}).get('message', 'Ошибка API')}"
    except Exception as e:
        reply = f"Ошибка: {str(e)}"
            
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": chat_id, "text": reply})
            
    return "ok", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
