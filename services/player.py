import aiohttp
import os

from services.state import (
    update_state,
    clear_state
)


LAVALINK_HOST = os.getenv("LAVALINK_HOST", "127.0.0.1")
LAVALINK_PORT = int(os.getenv("LAVALINK_PORT", "8080"))
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD", "musicapi")


def player_url(session_id: str, guild_id: str):
    return (
        f"http://{LAVALINK_HOST}:{LAVALINK_PORT}"
        f"/v4/sessions/{session_id}/players/{guild_id}"
    )


async def request_player(
    session_id: str,
    guild_id: str,
    payload: dict
):
    url = player_url(session_id, guild_id)

    headers = {
        "Authorization": LAVALINK_PASSWORD,
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.patch(
            url,
            headers=headers,
            json=payload
        ) as response:

            try:
                data = await response.json()
            except Exception:
                data = await response.text()

            return {
                "status_code": response.status,
                "data": data
            }


async def play(
    session_id: str,
    guild_id: str,
    track: dict
):
    encoded = track.get("encoded")

    if not encoded:
        return {
            "status_code": 400,
            "data": {
                "error": "Track has no encoded data"
            }
        }

    result = await request_player(
        session_id,
        guild_id,
        {
            "track": {
                "encoded": encoded
            },
            "paused": False
        }
    )

    if result["status_code"] < 300:
        update_state(
            guild_id,
            track=track,
            playing=True,
            paused=False,
            position=0
        )

    return result


async def pause(
    session_id: str,
    guild_id: str,
    paused: bool
):
    result = await request_player(
        session_id,
        guild_id,
        {
            "paused": paused
        }
    )

    if result["status_code"] < 300:
        update_state(
            guild_id,
            paused=paused,
            playing=not paused
        )

    return result


async def stop(
    session_id: str,
    guild_id: str
):
    result = await request_player(
        session_id,
        guild_id,
        {
            "track": {
                "encoded": None
            }
        }
    )

    if result["status_code"] < 300:
        clear_state(guild_id)

    return result


async def volume(
    session_id: str,
    guild_id: str,
    value: int
):
    result = await request_player(
        session_id,
        guild_id,
        {
            "volume": value
        }
    )

    if result["status_code"] < 300:
        update_state(
            guild_id,
            volume=value
        )

    return result


async def seek(
    session_id: str,
    guild_id: str,
    position: int
):
    result = await request_player(
        session_id,
        guild_id,
        {
            "position": position
        }
    )

    if result["status_code"] < 300:
        update_state(
            guild_id,
            position=position
        )

    return result