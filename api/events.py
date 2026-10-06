from fastapi import APIRouter
from services.playback import play_next


router = APIRouter()


@router.post("/events/track-end")
async def track_end(
    guild_id: str,
    session_id: str
):
    return await play_next(
        guild_id,
        session_id
    )
