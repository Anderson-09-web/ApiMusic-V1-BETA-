import aiohttp
import os
from urllib.parse import quote

LAVALINK_HOST = os.getenv("LAVALINK_HOST", "127.0.0.1")
LAVALINK_PORT = int(os.getenv("LAVALINK_PORT", "8080"))
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD", "musicapi")


async def search_tracks(query: str):
    identifier = f"ytsearch:{query}"

    url = (
        f"http://{LAVALINK_HOST}:{LAVALINK_PORT}"
        f"/v4/loadtracks?identifier={quote(identifier)}"
    )

    headers = {
        "Authorization": LAVALINK_PASSWORD
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:

            text = await response.text()

            if response.status != 200:
                return {
                    "error": "Lavalink error",
                    "status_code": response.status,
                    "details": text
                }

            try:
                data = await response.json()
            except Exception:
                return {
                    "error": "Invalid Lavalink response",
                    "status_code": response.status,
                    "details": text
                }

            tracks = data.get("data") or []

            results = []

            for track in tracks:
                info = track.get("info", {})

                results.append({
                    "encoded": track.get("encoded"),
                    "title": info.get("title"),
                    "author": info.get("author"),
                    "duration": info.get("length"),
                    "identifier": info.get("identifier"),
                    "url": info.get("uri"),
                    "artwork": info.get("artworkUrl"),
                    "source": info.get("sourceName")
                })

            return {
                "query": query,
                "loadType": data.get("loadType"),
                "results": results
            }
