import httpx

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

async def run_stream(file, stream_type):
    if stream_type == "Audio":
        return file
    raise ValueError(f"Unsupported stream type: {stream_type}")
