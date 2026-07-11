import os
import requests
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    print(f"Пришли данные: {data}") # Это теперь точно появится в логах!
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')
        TOKEN = os.environ.get("TOKEN")
        GEMINI_KEY = os.environ.get("GEMINI_KEY")
        
        # Запрос к Gemini
        resp = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}",
                             json={"contents": [{"parts": [{"text": text}]}]})
        
        if resp.status_code == 200:
            reply = resp.json()['candidates'][0]['content']['parts'][0]['text']
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": chat_id, "text": reply})
    return "ok", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
