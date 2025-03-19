from flask import Flask, request, jsonify
import requests
import telebot
import threading

app = Flask(__name__)

# عنوان سيرفر Node.js
NODE_SERVER_URL = 'https://xaz-node-js-oll.vercel.app/:3000'

# تخزين البوتات
bots = {}

# دالة لإرسال التوكن و ID الإداري إلى سيرفر Node.js
def send_to_node_server(token, admin_id):
    url = f'{NODE_SERVER_URL}/addToken'
    data = {'token': token, 'adminId': admin_id}
    response = requests.post(url, json=data)
    return response.json()

# دالة لبدء تشغيل البوت
def start_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        user_id = message.from_user.id
        message_text = message.text

        if str(user_id) in bots[token]['admins']:
            response_text = f"**تم استلام رسالة من الإداري:**\n{message_text}"
        else:
            response_text = "**تم ارسال طلب للسرفر وقريبن سوف يتم اضافت هذا البوت لسرفر XAZ, يرجي الانتظار مهلة من زمن🤖**"

        bot.reply_to(message, response_text, parse_mode='Markdown')

    # بدء الاستماع للرسائل
    bot.polling(none_stop=True)

# API لإضافة توكن و ID الإداري
@app.route('/add_bot', methods=['POST'])
def add_bot():
    data = request.json
    token = data.get('token')
    admin_id = data.get('admin_id')

    if not token or not admin_id:
        return jsonify({'error': 'Token and Admin ID are required'}), 400

    # إرسال التوكن و ID الإداري إلى سيرفر Node.js
    node_response = send_to_node_server(token, admin_id)
    if 'error' in node_response:
        return jsonify(node_response), 400

    # تخزين البوت وبدء تشغيله
    bots[token] = {'admins': [admin_id]}
    threading.Thread(target=start_bot, args=(token,)).start()

    return jsonify({'message': 'Bot added successfully', 'token': token, 'admin_id': admin_id})

# تشغيل السيرفر
if __name__ == '__main__':
    app.run(port=5000)
