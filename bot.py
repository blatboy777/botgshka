import os
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    print("Сообщение получено!") # Это появится в логах Render
    return "ok", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
