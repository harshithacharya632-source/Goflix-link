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
from info import *
from utils import temp
from Script import script 
from datetime import date, datetime 
from aiohttp import web
from plugins import web_server

from TechVJ.bot import TechVJBot
from TechVJ.util.keepalive import ping_server

# ✅ ADD THIS IMPORT
from channel_utils import send_restart_message, test_channel_access

async def start():
    print('\n')
    print('🚀 Initializing FileToLink Bot...')
    
    # Validate required environment variables
    if not API_ID or not API_HASH or not BOT_TOKEN:
        print("❌ Error: Missing required environment variables (API_ID, API_HASH, BOT_TOKEN)")
        return
    
    # Start the bot
    try:
        await TechVJBot.start()
        bot_info = await TechVJBot.get_me()
        print(f"✅ Bot started as @{bot_info.username}")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        return
    
    # ✅ TEST CHANNEL ACCESS
    channel_test = await test_channel_access(TechVJBot)
    print(f"🔧 {channel_test}")
    
    # Load plugins
    ppath = "plugins/*.py"
    files = glob.glob(ppath)
    
    if not files:
        print("❌ No plugins found in plugins/ directory")
    else:
        for name in files:
            try:
                patt = Path(name)
                plugin_name = patt.stem.replace(".py", "")
                import_path = f"plugins.{plugin_name}"
                
                # Import the plugin
                spec = importlib.util.spec_from_file_location(import_path, name)
                load = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(load)
                sys.modules[import_path] = load
                print(f"✅ Imported => {plugin_name}")
            except Exception as e:
                print(f"❌ Failed to import {plugin_name}: {e}")
    
    # Setup temp variables
    me = await TechVJBot.get_me()
    temp.BOT = TechVJBot
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    temp.B_LINK = f"https://t.me/{me.username}" if me.username else None
    
    # ✅ FIXED: Send restart message safely
    try:
        tz = pytz.timezone('Asia/Kolkata')
        today = date.today()
        now = datetime.now(tz)
        time = now.strftime("%H:%M:%S %p")
        
        restart_msg = script.RESTART_TXT.format(today, time)
        
        # ✅ USE SAFE CHANNEL FUNCTION INSTEAD OF DIRECT SEND
        success = await send_restart_message(TechVJBot, restart_msg)
        if success:
            print("✅ Restart message sent successfully")
        else:
            print("⚠️ Restart message sent to admin fallback")
            
    except Exception as e:
        print(f"⚠️ Could not send restart message: {e}")
    
    # Start keepalive server if on Heroku/Render
    if ON_HEROKU:
        asyncio.create_task(ping_server())
        print("✅ Keepalive server started")
    
    # Start web server
    try:
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        port = int(PORT) if PORT else 8080
        await web.TCPSite(app, bind_address, port).start()
        print(f"✅ Web server started on port {port}")
    except Exception as e:
        print(f"⚠️ Web server error: {e}")
    
    print("🎉 Bot is now running! Press Ctrl+C to stop.")
    print(f"🔗 Your bot: https://t.me/{me.username}")
    
    # Keep the bot running
    await idle()

if __name__ == '__main__':
    try:
        # Create new event loop for Render
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        print('\n👋 Service Stopped Bye!')
    except Exception as e:
        print(f'\n❌ Error: {e}')
