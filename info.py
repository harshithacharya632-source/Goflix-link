import re
import os
from os import environ

id_pattern = re.compile(r'^.\d+$')

# Bot information
SESSION = environ.get('SESSION', 'TechVJBot')
API_ID = int(environ.get('API_ID', ''))
API_HASH = environ.get('API_HASH', '')
BOT_TOKEN = environ.get('BOT_TOKEN', "")

# Bot settings
PORT = environ.get("PORT", "8080")

# Online Stream and Download
MULTI_CLIENT = False
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))
ON_HEROKU = 'DYNO' in environ
URL = environ.get("URL", "https://goflix-link.onrender.com")

# Admins, Channels & Users - FIX THESE
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1001234567890'))  # Add your actual channel ID
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '1234567890').split()]  # Add your admin ID

# MongoDB information
DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://harshithacharya632:j2UBud9b3XUpk4Pn@goflix.iff0agy.mongodb.net/goflix?retryWrites=true&w=majority&appName=Goflix")
DATABASE_NAME = environ.get('DATABASE_NAME', "Goflix")

# Shortlink Info
SHORTLINK = environ.get('SHORTLINK', 'False').lower() == 'true'
SHORTLINK_URL = environ.get('SHORTLINK_URL', 'api.shareus.io')
SHORTLINK_API = environ.get('SHORTLINK_API', 'hRPS5vvZc0OGOEUQJMJzPiojoVK2')

# Debug: Check if variables are loading
print("=== Environment Variables ===")
print(f"API_ID: {API_ID}")
print(f"LOG_CHANNEL: {LOG_CHANNEL}")
print(f"ADMINS: {ADMINS}")
print("=============================")
