import re
import os
from os import environ

id_pattern = re.compile(r'^.\d+$')

# Bot information
SESSION = environ.get('SESSION', 'TechVJBot')
API_ID = int(environ.get('API_ID', '0'))
API_HASH = environ.get('API_HASH', '')
BOT_TOKEN = environ.get('BOT_TOKEN', "")

print("=== 🔧 Goflix Bot Starting ===")

# ✅ IMMEDIATE FIX: Handle LOG_CHANNEL properly
log_channel_str = environ.get('LOG_CHANNEL', '').strip()

# If LOG_CHANNEL is empty or invalid, disable it temporarily
if not log_channel_str:
    LOG_CHANNEL = None
    print("⚠️ LOG_CHANNEL not set - disabling channel logs")
else:
    try:
        LOG_CHANNEL = int(log_channel_str)
        # Validate if it's a proper channel ID (should start with -100)
        if str(LOG_CHANNEL).startswith('-100'):
            print(f"✅ LOG_CHANNEL set to: {LOG_CHANNEL}")
        else:
            print(f"⚠️ LOG_CHANNEL may be invalid (should start with -100): {LOG_CHANNEL}")
            LOG_CHANNEL = None
    except ValueError:
        print(f"❌ Invalid LOG_CHANNEL format, disabling: {log_channel_str}")
        LOG_CHANNEL = None

# Bot settings
PORT = environ.get("PORT", "8080")

# Admins - using YOUR user ID from the error message
ADMINS = []
admins_str = environ.get('ADMINS', '')
if admins_str:
    ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in admins_str.split()]
else:
    ADMINS = [7011228023]  # ← YOUR User ID from the error message
    print(f"✅ ADMINS set to your ID: {ADMINS}")

# Other configurations
MULTI_CLIENT = False
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))
ON_HEROKU = 'DYNO' in environ
URL = environ.get("URL", "https://goflix-link-bot01.onrender.com")

# MongoDB
DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://harshithacharya632:j2UBud9b3XUpk4Pn@goflix.iff0agy.mongodb.net/goflix?retryWrites=true&w=majority&appName=Goflix")
DATABASE_NAME = environ.get('DATABASE_NAME', "Goflix")

# Shortlink
SHORTLINK = environ.get('SHORTLINK', 'False').lower() == 'true'
SHORTLINK_URL = environ.get('SHORTLINK_URL', 'api.shareus.io')
SHORTLINK_API = environ.get('SHORTLINK_API', 'hRPS5vvZc0OGOEUQJMJzPiojoVK2')

print("=== ✅ Configuration Loaded Successfully ===")
