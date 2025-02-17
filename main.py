import time
import pymongo
import requests
import os
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bot Configuration
API_ID = 27796607
API_HASH = "56d68cab1e7c1a8e64ea7e77383cec84"
BOT_TOKEN = "7957099017:AAEv1Qkw3dlTwP5f9UJeEepNpKSU0CRmoNg"
MONGO_URL = "mongodb+srv://itfeel469:Xn1dAIDqHKhb0pGz@cluster0.gs9yv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "itfeel469"
PORT = int(os.environ.get("PORT", 8080))

# Link Shortener APIs
AROLINKS_API = "67e76cbd040936bca1cfd2944edb65754bac2361"
TELEGRAMLINK_API = "4fc9c8bf2c102c7a32d4977e56736073d411d326"

# Force Subscribe Channels
FORCE_SUB_CHANNELS = ["-1002259746210", "-1002435598484"]

# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client[DB_NAME]
users_collection = db["verified_users"]

# Initialize Bot
bot = Client("TokenVerificationBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running..."

def shorten_url(api, url):
    response = requests.get(f"https://{api.split('_')[0]}.com/api?api={api}&url={url}")
    return response.json().get("shortenedUrl", url)

@bot.on_message(filters.command("start"))
def start(client, message):
    user_id = message.from_user.id
    user = users_collection.find_one({"user_id": user_id})
    if user and time.time() < user["expires"]:
        message.reply_text("✅ You are already verified!")
        return
    
    # First Step Verification
    long_url = f"https://t.me/tutto_rri/14"
    short_url = shorten_url(AROLINKS_API, long_url)
    button = [[InlineKeyboardButton("Verify Now", url=short_url)]]
    
    message.reply_text(
        "🔹 Click the button below to complete first verification.\n⚠️ Valid for 12 hours.",
        reply_markup=InlineKeyboardMarkup(button)
    )
    
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"expires": time.time() + 43200}},  # 12 hours
        upsert=True
    )

@bot.on_message(filters.command("verify"))
def verify(client, message):
    user_id = message.from_user.id
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        message.reply_text("⚠️ Please complete first verification using /start")
        return
    if time.time() < user["expires"]:
        message.reply_text("✅ You are already verified!")
        return
    
    # Second Step Verification
    long_url = f"https://t.me/tutto_rri/15"
    short_url = shorten_url(TELEGRAMLINK_API, long_url)
    button = [[InlineKeyboardButton("Verify Again", url=short_url)]]
    
    message.reply_text(
        "🔹 Complete second verification to extend access for another 12 hours.",
        reply_markup=InlineKeyboardMarkup(button)
    )
    
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"expires": time.time() + 43200}},  # 12 more hours
        upsert=True
    )

@bot.on_message(filters.command("addchannel") & filters.user(7913251938))
def add_channel(client, message):
    global FORCE_SUB_CHANNELS
    try:
        channel_id = message.text.split()[1]
        if channel_id not in FORCE_SUB_CHANNELS:
            FORCE_SUB_CHANNELS.append(channel_id)
            message.reply_text(f"✅ Channel {channel_id} added to force subscription list.")
        else:
            message.reply_text("⚠️ Channel already exists.")
    except IndexError:
        message.reply_text("⚠️ Usage: /addchannel <channel_id>")

@bot.on_message(filters.command("removechannel") & filters.user(7913251938))
def remove_channel(client, message):
    global FORCE_SUB_CHANNELS
    try:
        channel_id = message.text.split()[1]
        if channel_id in FORCE_SUB_CHANNELS:
            FORCE_SUB_CHANNELS.remove(channel_id)
            message.reply_text(f"✅ Channel {channel_id} removed from force subscription list.")
        else:
            message.reply_text("⚠️ Channel not found.")
    except IndexError:
        message.reply_text("⚠️ Usage: /removechannel <channel_id>")

@bot.on_message(filters.command("listchannels") & filters.user(7913251938))
def list_channels(client, message):
    channels = '\n'.join(FORCE_SUB_CHANNELS)
    message.reply_text(f"📌 Force Subscribe Channels:\n{channels}")

if __name__ == "__main__":
    print("Bot is running...")
    bot.start()
    app.run(host="0.0.0.0", port=PORT)
