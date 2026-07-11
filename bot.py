import os
import requests
from flask import Flask, request
import google.generativeai as genai

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
    
    reply = ""
    try:
        # Настраиваем SDK с принудительным использованием стабильной версии v1
        genai.configure(api_key=GEMINI_KEY, api_version='v1')
        
        # Используем модель, которая в v1 доступна всем
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(text)
        
        reply = response.text
    except Exception as e:
        reply = f"Ошибка SDK v1: {str(e)}"
            
    # Отправка ответа
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": chat_id, "text": reply})
            
    return "ok", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
