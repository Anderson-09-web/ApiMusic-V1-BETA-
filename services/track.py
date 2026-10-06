import aiohttp
import os

LAVALINK_HOST = os.getenv("LAVALINK_HOST", "127.0.0.1")
LAVALINK_PORT = int(os.getenv("LAVALINK_PORT", "8080"))
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD", "musicapi")


async def get_track(identifier: str):
    url = (
        f"http://{LAVALINK_HOST}:{LAVALINK_PORT}"
        f"/v4/loadtracks?identifier=ytsearch:{identifier}"
    )

    headers = {
        "Authorization": LAVALINK_PASSWORD
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()

            if response.status != 200:
                return {
                    "error": "Lavalink error",
                    "status_code": response.status,
                    "details": data
                }

            tracks = data.get("data", [])

            if not tracks:
                return {
                    "error": "Track not found"
                }

            track = tracks[0]
            info = track.get("info", {})

            return {
                "encoded": track.get("encoded"),
                "title": info.get("title"),
                "author": info.get("author"),
                "duration": info.get("length"),
                "identifier": info.get("identifier"),
                "url": info.get("uri"),
                "artwork": info.get("artworkUrl"),
                "source": info.get("sourceName")
            }
