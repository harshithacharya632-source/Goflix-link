# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import re, math, logging, secrets, mimetypes
from info import *
from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine
from TechVJ.bot import multi_clients, work_loads
from TechVJ.server.exceptions import FIleNotFound, InvalidHash
from TechVJ.util.time_format import get_readable_time
from TechVJ.util.render_template import render_page

routes = web.RouteTableDef()

# Replace with your private source channel ID (-100xxxxxxxx)
SOURCE_CHANNEL_ID = -1002954653440 -1001545302652  

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("BenFilterBot")

@routes.get(r"/watch/{path:\S+}", allow_head=True)
async def stream_page(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            msg_id = int(match.group(2))
        else:
            msg_id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")
        return web.Response(text=await render_page(msg_id, secure_hash), content_type='text/html')
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e, exc_info=True)
        raise web.HTTPInternalServerError(text=str(e))

@routes.get(r"/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            msg_id = int(match.group(2))
        else:
            msg_id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")
        return await media_streamer(request, msg_id, secure_hash)
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e, exc_info=True)
        raise web.HTTPInternalServerError(text=str(e))


class_cache = {}

async def media_streamer(request: web.Request, msg_id: int, secure_hash: str):
    range_header = request.headers.get("Range", 0)

    # Pick least busy client
    index = min(work_loads, key=work_loads.get)
    client = multi_clients[index]

    # Get the original message from private channel
    msg = await client.get_messages(chat_id=SOURCE_CHANNEL_ID, message_ids=msg_id)
    if not msg or not (msg.video or msg.document):
        raise FIleNotFound("❌ File not found in private channel.")

    media = msg.video or msg.document

    # Verify hash
    if media.file_unique_id[:6] != secure_hash:
        logging.debug(f"Invalid hash for message ID {msg_id}")
        raise InvalidHash

    file_size = media.file_size
    mime_type = media.mime_type
    file_name = media.file_name

    if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = 0
        until_bytes = file_size - 1

    if (until_bytes > file_size) or (from_bytes < 0) or (until_bytes < from_bytes):
        return web.Response(
            status=416,
            body="416: Range not satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"},
        )

    chunk_size = 1024 * 1024
    until_bytes = min(until_bytes, file_size - 1)

    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1

    req_length = until_bytes - from_bytes + 1
    part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)

    # Stream the file directly from Telegram (no CDN)
    from TechVJ.util.custom_dl import ByteStreamer
    if client not in class_cache:
        class_cache[client] = ByteStreamer(client)
    tg_connect = class_cache[client]

    body = tg_connect.yield_file(
        media,
        index,
        offset,
        first_part_cut,
        last_part_cut,
        part_count,
        chunk_size
    )

    # File info defaults
    if not file_name:
        ext = mime_type.split("/")[1] if mime_type else "bin"
        file_name = f"{secrets.token_hex(2)}.{ext}"
    if not mime_type:
        mime_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"

    return web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": mime_type,
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(req_length),
            "Content-Disposition": f'inline; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        },
    )
