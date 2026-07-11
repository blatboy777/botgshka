import os
import requests
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return "Бот DeepSeek работает!", 200
        
    data = request.json
    if not data or 'message' not in data:
        return "ok", 200
        
    chat_id = data['message']['chat']['id']
    text = data['message'].get('text', '...')
    
    TOKEN = os.environ.get("TOKEN")
    # Твой новый ключ DeepSeek
    DEEPSEEK_KEY = os.environ.get("DEEPSEEK_KEY")
    
    # URL API DeepSeek
    url = "https://api.deepseek.com/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": text}],
        "stream": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        res_data = response.json()
        
        if response.status_code == 200:
            reply = res_data['choices'][0]['message']['content']
        else:
            reply = f"Ошибка DeepSeek ({response.status_code}): {res_data.get('error', {}).get('message', 'Неизвестная ошибка')}"
            
    except Exception as e:
        reply = f"Системная ошибка: {str(e)}"
            
    # Отправка ответа в Telegram
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": chat_id, "text": reply})
            
    return "ok", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
