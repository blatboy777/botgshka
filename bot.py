import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Твой ID, который ты прислал
MY_ID = "1717246201"

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    if not data or 'message' not in data:
        return "ok", 200
        
    message = data['message']
    chat_id = message['chat']['id']
    sender_name = message['from'].get('first_name', 'Неизвестный')
    text = message.get('text', '')
    
    TOKEN = os.environ.get("TOKEN")
    API_KEY = os.environ.get("YANDEX_API_KEY")
    FOLDER_ID = os.environ.get("YANDEX_FOLDER_ID")
    
    # Бот игнорирует сообщения от тебя, чтобы не было зацикливания
    if str(chat_id) == MY_ID:
        return "ok", 200

    # Запрос к YandexGPT для анализа входящего сообщения
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {"Authorization": f"Api-Key {API_KEY}", "x-folder-id": FOLDER_ID}
    
    payload = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {"temperature": 0.3},
        "messages": [
            {"role": "system", "text": "Ты личный секретарь. Анализируй сообщение: кто пишет, суть, степень срочности. Предложи вариант ответа."},
            {"role": "user", "text": text}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload).json()
        analysis = response['result']['alternatives'][0]['message']['text']
    except Exception as e:
        analysis = f"Не удалось проанализировать сообщение: {str(e)}"
    
    # Отправляем отчет ТЕБЕ
    notification = f"📩 Новое сообщение от {sender_name}:\n{text}\n\n🤖 Анализ:\n{analysis}"
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": MY_ID, "text": notification})
            
    return "ok", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
