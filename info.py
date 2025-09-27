import re
from os import environ

# Regex to validate Telegram IDs
id_pattern = re.compile(r'^.\d+$')

# ----------------------------
# Bot Information
# ----------------------------
SESSION = environ.get('SESSION', 'TechVJBot')
API_ID = int(environ.get('API_ID', ''))
API_HASH = environ.get('API_HASH', '')
BOT_TOKEN = environ.get('BOT_TOKEN', "")

# ----------------------------
# Flask / App Settings
# ----------------------------
PORT = environ.get("PORT", "8080")
URL = environ.get("URL", "https://goflix-link-bot01.onrender.com")

# ----------------------------
# Online Stream and Download Settings
# ----------------------------
MULTI_CLIENT = False
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))  # 20 minutes
ON_HEROKU = 'DYNO' in environ

# ----------------------------
# Admins, Channels & Users
# ----------------------------
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1003059886878'))
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '').split()]

# ----------------------------
# MongoDB Information
# ----------------------------
DATABASE_URI = environ.get(
    'DATABASE_URI',
    "mongodb+srv://harshithacharya632:j2UBud9b3XUpk4Pn@goflix.iff0agy.mongodb.net/goflix?retryWrites=true&w=majority&appName=Goflix"
)
DATABASE_NAME = environ.get('DATABASE_NAME', "Goflix")

# ----------------------------
# Shortlink Info
# ----------------------------
SHORTLINK = bool(environ.get('SHORTLINK', False))  # Set True Or False
SHORTLINK_URL = environ.get('SHORTLINK_URL', 'api.shareus.io')
SHORTLINK_API = environ.get('SHORTLINK_API', 'hRPS5vvZc0OGOEUQJMJzPiojoVK2')
