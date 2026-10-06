from services.queue import pop_next
from services.player import play


async def play_next(
    guild_id: str,
    session_id: str
):
    track = pop_next(guild_id)

    if track is None:
        return {
            "status": "empty",
            "message": "Queue is empty"
        }

    encoded = track.get("encoded")

    if not encoded:
        return {
            "status": "error",
            "message": "Track has no encoded data"
        }

    result = await play(
        session_id,
        guild_id,
        encoded
    )

    return {
        "status": "playing",
        "track": track,
        "player": result
    }
