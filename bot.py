import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Твой ID, чтобы бот не отвечал сам себе (защита от цикла)
MY_ID = "1717246201"

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    # В Telegram Business приходят разные типы данных, проверяем наличие сообщения
    if not data or 'business_message' not in data:
        return "ok", 200
        
    msg = data['business_message']
    chat_id = msg['chat']['id']
    text = msg.get('text', '')
    
    # 1. Защита от зацикливания
    if str(msg['from']['id']) == MY_ID:
        return "ok", 200

    # 2. Получаем ключи
    TOKEN = os.environ.get("TOKEN")
    API_KEY = os.environ.get("YANDEX_API_KEY")
    FOLDER_ID = os.environ.get("YANDEX_FOLDER_ID")
    
    # 3. Запрос к YandexGPT для генерации ответа
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {"Authorization": f"Api-Key {API_KEY}", "x-folder-id": FOLDER_ID}
    
    payload = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {"temperature": 0.6},
        "messages": [
            {"role": "system", "text": "Ты — Казбек (личный секретарь). Отвечай вежливо и кратко от первого лица на сообщения собеседника."},
            {"role": "user", "text": text}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload).json()
        reply = response['result']['alternatives'][0]['message']['text']
    except Exception as e:
        reply = "Извините, я сейчас не могу ответить."
    
    # 4. ОТВЕТ ЧЕЛОВЕКУ (используем sendMessage в чат отправителя)
    # Telegram Business работает через обычный API ботов
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": chat_id, "text": reply})
            
    return "ok", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
