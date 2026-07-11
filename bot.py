import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Переменная для сохранения найденной рабочей модели
WORKING_MODEL = None

def get_working_model(api_key):
    global WORKING_MODEL
    if WORKING_MODEL:
        return WORKING_MODEL
        
    # Спрашиваем у Google список всех доступных моделей для твоего ключа
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            models_data = resp.json().get('models', [])
            for m in models_data:
                # Ищем первую модель Gemini, которая поддерживает генерацию текста
                if 'generateContent' in m.get('supportedGenerationMethods', []) and 'gemini' in m.get('name', '').lower():
                    WORKING_MODEL = m['name']
                    return WORKING_MODEL
    except Exception:
        pass
        
    return "models/gemini-1.5-flash" # Резервный вариант

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
    
    # Автоматически получаем правильное имя модели
    model_name = get_working_model(GEMINI_KEY)
    
    # Формируем точный URL
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={GEMINI_KEY}"
    
    try:
        resp = requests.post(url, json={"contents": [{"parts": [{"text": text}]}]})
        if resp.status_code == 200:
            reply = resp.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            try:
                error_details = resp.json().get('error', {}).get('message', f"Код {resp.status_code}")
                reply = f"Ошибка Gemini {resp.status_code} (Модель: {model_name}): {error_details}"
            except:
                reply = f"Ошибка API Gemini: {resp.status_code}"
    except Exception as e:
        reply = f"Системная ошибка: {str(e)}"
            
    # Отправляем результат обратно в Telegram
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": chat_id, "text": reply})
            
    return "ok", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
