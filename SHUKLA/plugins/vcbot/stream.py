from pyrogram import filters
from pytgcalls.exceptions import GroupCallNotFound

from ... import app, call, cdz, eor, sudo_users_only
from ...modules.utilities.queues import queues
from ...modules.utilities.stream import get_stream_url, run_stream

@app.on_message(cdz(["ply", "play"]) & ~filters.private)
@sudo_users_only
async def audio_stream(client, message):
    chat_id = message.chat.id
    aux = await eor(message, "**Processing ...**")
    audio = (
        message.reply_to_message.audio or message.reply_to_message.voice
        if message.reply_to_message
        else None
    )
    stream_type = "Audio"
    try:
        if audio:
            await aux.edit("Downloading ...")
            file = await client.download_media(message.reply_to_message)
        else:
            if len(message.command) < 2:
                return await aux.edit("**🥀 Give me a query to play music❗**")
            query = message.text.split(None, 1)[1].split("?si=")[0] if "?si=" in message.text else message.text.split(None, 1)[1]
            await aux.edit("Fetching stream ...")
            file = await get_stream_url(query, video=False)
            if not file:
                return await aux.edit("**Failed to fetch stream URL. Try again!**")
        try:
            a = await call.get_call(chat_id)
            if a.status == "not_playing":
                stream = await run_stream(file, stream_type)
                await call.change_stream(chat_id, stream)
                await aux.edit("Playing!")
            elif a.status in ("playing", "paused"):
                position = await queues.put(chat_id, file=file, type=stream_type)
                await aux.edit(f"Queued at position {position}")
        except GroupCallNotFound:
            stream = await run_stream(file, stream_type)
            await call.join_group_call(chat_id, stream)
            await aux.edit("Playing!")
    except Exception as e:
        print(f"Error: {e}")
        await aux.edit("**An error occurred. Please try again!**")
