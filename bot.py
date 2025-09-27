# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import sys, glob, importlib, logging, logging.config, pytz, asyncio
from pathlib import Path

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

from pyrogram import idle 
from database.users_chats_db import db
from info import *
from utils import temp
from Script import script 
from datetime import date, datetime 
from aiohttp import web
from plugins import web_server

from TechVJ.bot import TechVJBot
from TechVJ.util.keepalive import ping_server
from TechVJ.bot.clients import initialize_clients

async def start():
    print('\n')
    print('Initializing Your Bot')
    
    # Start the bot first
    await TechVJBot.start()
    bot_info = await TechVJBot.get_me()
    print(f"Bot started as @{bot_info.username}")
    
    await initialize_clients()
    
    # Load plugins
    ppath = "plugins/*.py"
    files = glob.glob(ppath)
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = "plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print("Tech VJ Imported => " + plugin_name)
    
    if ON_HEROKU:
        asyncio.create_task(ping_server())
    
    me = await TechVJBot.get_me()
    temp.BOT = TechVJBot
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")
    
    # Send restart message
    try:
        await TechVJBot.send_message(
            chat_id=LOG_CHANNEL, 
            text=script.RESTART_TXT.format(today, time)
        )
        print("✅ Restart message sent to log channel")
    except Exception as e:
        print(f"❌ Error sending restart message: {e}")
    
    # Start web server
    try:
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()
        print(f"✅ Web server started on port {PORT}")
    except Exception as e:
        print(f"❌ Error starting web server: {e}")
    
    print("✅ Bot is now running! Press Ctrl+C to stop.")
    await idle()

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        print('Service Stopped Bye 👋')
    except Exception as e:
        print(f'Error: {e}')
