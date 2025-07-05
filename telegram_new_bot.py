import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import os
import time
import sys
from flask import Flask, request, jsonify
import threading
import signal
import logging

# Configuration
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7973005069:AAGu59TgHahin9lLUpGOcBEVvDKAP3UOctI')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', '@AlphaX_ZoneOwner')
ADMIN_URL = os.environ.get('ADMIN_URL', 'https://t.me/AlphaX_ZoneOwner')
USERS_FILE = os.environ.get('USERS_FILE', 'users.txt')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Parse ADMIN_IDS safely
def parse_admin_ids():
    try:
        admin_ids_str = os.environ.get('ADMIN_IDS', '6220750783,6979809331')
        # Remove any brackets and extra spaces
        admin_ids_str = admin_ids_str.replace('[', '').replace(']', '').strip()
        return [int(x.strip()) for x in admin_ids_str.split(',') if x.strip().isdigit()]
    except Exception as e:
        print(f"Error parsing ADMIN_IDS, using default: {e}")
        return [6220750783, 6979809331]

ADMIN_IDS = parse_admin_ids()

bot = telebot.TeleBot(BOT_TOKEN)

# Flask app for web service
app = Flask(__name__)

# For broadcast mode
admin_broadcast_mode = set()

# Global variables for graceful shutdown
shutdown_event = threading.Event()

# Signal handler for graceful shutdown
def signal_handler(signum, frame):
    logger.info("Received shutdown signal. Gracefully shutting down...")
    shutdown_event.set()
    try:
        bot.delete_webhook()
    except:
        pass
    sys.exit(0)

# Function to check if bot is already running
def check_bot_status():
    try:
        bot_info = bot.get_me()
        logger.info(f"✅ Bot connected successfully: @{bot_info.username}")
        return True
    except Exception as e:
        logger.error(f"❌ Bot connection failed: {e}")
        return False

# Save user ID
def save_user(user_id):
    try:
        user_id = str(user_id)
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'w', encoding='utf-8') as f:
                f.write(user_id + '\n')
        else:
            with open(USERS_FILE, 'r+', encoding='utf-8') as f:
                users = set(line.strip() for line in f)
                if user_id not in users:
                    f.write(user_id + '\n')
    except Exception as e:
        logger.error(f"Error saving user: {e}")
        # Try to create file if it doesn't exist
        try:
            with open(USERS_FILE, 'w', encoding='utf-8') as f:
                f.write(user_id + '\n')
        except Exception as e2:
            logger.error(f"Failed to create users file: {e2}")

# /start command
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    name = message.from_user.first_name or "User"
    
    if user_id in ADMIN_IDS:
        # Create reply keyboard for admin commands
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("/start"),
            KeyboardButton("/broadcast")
        )
        markup.add(
            KeyboardButton("📊 Stats"),
            KeyboardButton("👥 Users")
        )
        bot.send_message(user_id, "You are an admin. Bot is working!\n\nআপনি অ্যাডমিন। বট ঠিকভাবে কাজ করছে!\n\nUse the buttons below:", reply_markup=markup)
    else:
        en_msg = f"Hi {name}! Please provide your key for tool approval"
        bn_msg = f"হ্যালো {name}! টুল অনুমোদনের জন্য আপনার কী দিন"
        bot.send_message(user_id, en_msg)
        bot.send_message(user_id, bn_msg)

# /broadcast command (admin only)
@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        bot.reply_to(message, "You are not authorized to use this command.")
        return
    # Show broadcast button
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Start Broadcast", callback_data="start_broadcast"))
    bot.send_message(user_id, "Click the button below and then send any text, photo, or voice to broadcast to all users:", reply_markup=markup)

# Handle admin button commands
@bot.message_handler(func=lambda message: message.text in ["📊 Stats", "👥 Users"])
def handle_admin_buttons(message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        return
    
    if message.text == "📊 Stats":
        total_users = 0
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, 'r', encoding='utf-8') as f:
                total_users = len(f.readlines())
            except Exception as e:
                logger.error(f"Error reading users file: {e}")
                total_users = 0
        bot.reply_to(message, f"📊 Bot Statistics:\n\n👥 Total Users: {total_users}\n🤖 Bot Status: Active")
    
    elif message.text == "👥 Users":
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users = f.readlines()
            except Exception as e:
                logger.error(f"Error reading users file: {e}")
                bot.reply_to(message, "Error reading users file.")
                return
            user_list = "\n".join([f"• {uid.strip()}" for uid in users[:10]])  # Show first 10 users
            if len(users) > 10:
                user_list += f"\n... and {len(users) - 10} more users"
            bot.reply_to(message, f"👥 User List:\n\n{user_list}")
        else:
            bot.reply_to(message, "No users have interacted with the bot yet.")

# Callback button handler
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    name = call.from_user.first_name or "User"
    
    if call.data == "price":
        en_msg = "Please contact admin"
        bn_msg = "\nঅ্যাডমিনের সাথে যোগাযোগ করুন"
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=en_msg + "\n" + bn_msg)
        except Exception as e:
            logger.error(f"Callback error: {e}")
    elif call.data == "start_broadcast":
        if user_id in ADMIN_IDS:
            admin_broadcast_mode.add(user_id)
            bot.answer_callback_query(call.id, "Broadcast mode enabled. Send any message now.")
            bot.send_message(user_id, "Broadcast mode enabled. Now send any text, photo, or voice message to broadcast to all users.")

# Admin broadcast handler
@bot.message_handler(func=lambda message: message.from_user.id in ADMIN_IDS and message.from_user.id in admin_broadcast_mode, content_types=['text', 'photo', 'document', 'audio', 'video', 'voice'])
def admin_broadcast_handler(message):
    user_id = message.from_user.id
    # Remove admin from broadcast mode after one message
    admin_broadcast_mode.discard(user_id)
    
    # Rate limiting - max 100 users per broadcast
    MAX_BROADCAST_USERS = 100
    # Send to all users except admins
    if not os.path.exists(USERS_FILE):
        bot.reply_to(message, "No users to broadcast to.")
        return
    count = 0
    failed = 0
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
        user_ids = [int(line.strip()) for line in f if line.strip().isdigit() and int(line.strip()) not in ADMIN_IDS]
        
        # Limit broadcast to max users
        if len(user_ids) > MAX_BROADCAST_USERS:
            user_ids = user_ids[:MAX_BROADCAST_USERS]
            bot.reply_to(message, f"⚠️ Broadcasting to first {MAX_BROADCAST_USERS} users only (rate limit protection)")
            
    except Exception as e:
        logger.error(f"Error reading users file for broadcast: {e}")
        bot.reply_to(message, "Error reading users file.")
        return
    for uid in user_ids:
        try:
            if message.content_type == 'text':
                bot.send_message(uid, message.text)
            elif message.content_type == 'photo':
                bot.send_photo(uid, message.photo[-1].file_id, caption=message.caption or "")
            elif message.content_type == 'document':
                bot.send_document(uid, message.document.file_id, caption=message.caption or "")
            elif message.content_type == 'audio':
                bot.send_audio(uid, message.audio.file_id, caption=message.caption or "")
            elif message.content_type == 'video':
                bot.send_video(uid, message.video.file_id, caption=message.caption or "")
            elif message.content_type == 'voice':
                bot.send_voice(uid, message.voice.file_id)
            count += 1
            
            # Rate limiting - small delay between messages
            time.sleep(0.1)
            
        except Exception as e:
            logger.error(f"Failed to send broadcast to {uid}: {e}")
            failed += 1
    bot.reply_to(message, f"Broadcast sent to {count} users. Failed: {failed}")

# Handle all normal messages (non-command)
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'document', 'audio', 'video', 'voice'])
def forward_to_admins(message):
    user = message.from_user
    user_id = user.id
    username = user.username or "Unknown"
    name = user.first_name or "User"

    # Save user
    save_user(user_id)

    # Only forward non-admin messages to admins
    if user_id not in ADMIN_IDS:
        # Forward to admins
        for admin_id in ADMIN_IDS:
            try:
                bot.forward_message(chat_id=admin_id, from_chat_id=message.chat.id, message_id=message.message_id)
                bot.send_message(admin_id, f"From user {user_id} (@{username})")
            except Exception as e:
                logger.error(f"Failed to forward to admin {admin_id}: {e}")

        # Reply to user (only for non-admin users)
        bot.send_message(user_id, f"Hi {name}! received✅.")

        en_msg = f"📞{name} Please contact the admin {ADMIN_USERNAME} to approve your key."
        bn_msg = f"🛠️ প্রিয় {name}, আপনার Key অনুমোদনের জন্য অনুগ্রহ করে অ্যাডমিন {ADMIN_USERNAME} এর সাথে যোগাযোগ করুন।"
        
        bot.send_message(user_id, en_msg)
        
        # Send Bangla message with Price and Contact buttons
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("💸 Price", callback_data="price"),
            InlineKeyboardButton("📞 Contact", url=ADMIN_URL)
        )
        bot.send_message(user_id, bn_msg, reply_markup=keyboard)

# Flask routes for web service
@app.route('/')
def home():
    return "🤖 Telegram Bot is running!"

@app.route('/health')
def health():
    return "OK"

@app.route('/status')
def status():
    try:
        bot_info = bot.get_me()
        return f"Bot Status: Active<br>Username: @{bot_info.username}"
    except Exception as e:
        return f"Bot Status: Error - {str(e)}"

@app.route('/api/check_key')
def check_key():
    key = request.args.get('key')
    if not key:
        return jsonify({'error': 'No key provided'}), 400
    
    # Auto wake up endpoint - accepts any key
    return jsonify({
        'key': key,
        'approved': True,
        'status': 'approved',
        'message': 'Service is awake and running'
    })

# Webhook endpoint for Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        try:
            update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
            if update:
                bot.process_new_updates([update])
            return 'ok', 200
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return 'error', 500

if __name__ == "__main__":
    logger.info("🤖 Bot is starting...")
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check bot status before starting
    if not check_bot_status():
        logger.error("❌ Bot initialization failed. Exiting...")
        sys.exit(1)
    
    # Start Flask web server first
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🌐 Starting web server on port {port}...")
    
    # Set webhook for the bot
    try:
        webhook_url = f"https://likhon-test-old-clone.onrender.com/webhook"
        bot.delete_webhook()  # Clear any existing webhook
        time.sleep(1)
        bot.set_webhook(url=webhook_url)
        logger.info(f"✅ Webhook set successfully: {webhook_url}")
    except Exception as e:
        logger.error(f"❌ Failed to set webhook: {e}")
        # Fallback to polling if webhook fails
        logger.info("🔄 Falling back to polling mode...")
        bot_thread = threading.Thread(target=lambda: bot.infinity_polling(timeout=60, long_polling_timeout=60), daemon=True)
        bot_thread.start()
    
    try:
    app.run(host='0.0.0.0', port=port, debug=False) 
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt. Shutting down...")
        shutdown_event.set()
        try:
            bot.delete_webhook()
        except:
            pass 