import asyncio
import os
import re
from typing import Union

import httpx
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
import yt_dlp

async def get_stream_url(query, video=False):
    api_url = "http://3.0.146.239:1470/youtube"
    api_key = "badmusic_ytstream_apikey_2025"
    async with httpx.AsyncClient(timeout=60) as client:
        params = {"query": query, "video": video, "api_key": api_key}
        response = await client.get(api_url, params=params)
        if response.status_code != 200:
            return ""
        info = response.json()
        return info.get("stream_url", "")

async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in errorz.decode("utf-8").lower():
            return out.decode("utf-8")
        return errorz.decode("utf-8")
    return out.decode("utf-8")

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message: Message) -> Union[str, None]:
        messages = [message]
        if message.reply_to_message:
            messages.append(message.reply_to_message)
        text = ""
        offset = None
        length = None
        for msg in messages:
            if offset:
                break
            if msg.entities:
                for entity in msg.entities:
                    if entity.type == MessageEntityType.URL:
                        text = msg.text or msg.caption
                        offset, length = entity.offset, entity.length
                        break
            elif msg.caption_entities:
                for entity in msg.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset is None:
            return None
        return text[offset:offset + length]

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        return await get_stream_url(link, True)

    async def audio(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        return await get_stream_url(link, False)

    async def playlist(self, link, limit, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        playlist = await shell_cmd(
            f"yt-dlp -i --compat-options no-youtube-unavailable-videos "
            f"--get-id --flat-playlist --playlist-end {limit} --skip-download \"{link}\" 2>/dev/null"
        )
        try:
            result = [key for key in playlist.split("\n") if key]
        except Exception:
            result = []
        return result
