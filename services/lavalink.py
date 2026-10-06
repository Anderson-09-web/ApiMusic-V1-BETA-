import aiohttp
import os

LAVALINK_HOST = os.getenv("LAVALINK_HOST", "127.0.0.1")
LAVALINK_PORT = int(os.getenv("LAVALINK_PORT", "8080"))
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD", "musicapi")


async def get_lavalink_version():
    url = f"http://{LAVALINK_HOST}:{LAVALINK_PORT}/version"

    headers = {
        "Authorization": LAVALINK_PASSWORD
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return {
                "status_code": response.status,
                "version": await response.text()
            }
