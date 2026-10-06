from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

from api.events import router as events_router

from services.playback import play_next
from services.lavalink import get_lavalink_version
from services.search import search_tracks
from services.track import get_track

from services.player import (
    play,
    pause,
    stop,
    volume,
    seek
)

from services.queue import (
    get_queue,
    add_to_queue,
    clear_queue,
    remove_from_queue
)

from services.state import get_state


app = FastAPI(
    title="Music API",
    description="API de música para Discord basada en Lavalink",
    version="1.0.0"
)


# =========================
# EVENTOS
# =========================

app.include_router(events_router)


# =========================
# MODELOS
# =========================

class PlayRequest(BaseModel):
    session_id: str
    track: dict


class PauseRequest(BaseModel):
    session_id: str
    paused: bool


class PlayerRequest(BaseModel):
    session_id: str


class VolumeRequest(BaseModel):
    session_id: str
    volume: int = Field(..., ge=0, le=1000)


class SeekRequest(BaseModel):
    session_id: str
    position: int = Field(..., ge=0)


# =========================
# GENERAL
# =========================

@app.get("/")
async def root():
    return {
        "name": "Music API",
        "version": "1.0.0",
        "status": "online"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }


@app.get("/lavalink")
async def lavalink():
    return await get_lavalink_version()


# =========================
# SEARCH
# =========================

@app.get("/search")
async def search(query: str = Query(..., min_length=1)):
    return await search_tracks(query)


@app.get("/track/{identifier}")
async def track(identifier: str):
    return await get_track(identifier)


# =========================
# PLAYER
# =========================

@app.post("/player/{guild_id}/play")
async def player_play(
    guild_id: str,
    request: PlayRequest
):
    return await play(
        request.session_id,
        guild_id,
        request.track
    )


@app.post("/player/{guild_id}/pause")
async def player_pause(
    guild_id: str,
    request: PauseRequest
):
    return await pause(
        request.session_id,
        guild_id,
        request.paused
    )


@app.post("/player/{guild_id}/stop")
async def player_stop(
    guild_id: str,
    request: PlayerRequest
):
    return await stop(
        request.session_id,
        guild_id
    )


@app.post("/player/{guild_id}/volume")
async def player_volume(
    guild_id: str,
    request: VolumeRequest
):
    return await volume(
        request.session_id,
        guild_id,
        request.volume
    )


@app.post("/player/{guild_id}/seek")
async def player_seek(
    guild_id: str,
    request: SeekRequest
):
    return await seek(
        request.session_id,
        guild_id,
        request.position
    )


@app.get("/player/{guild_id}/state")
async def player_state(guild_id: str):
    return get_state(guild_id)


# =========================
# QUEUE
# =========================

@app.get("/queue/{guild_id}")
async def queue_get(guild_id: str):
    return {
        "guild_id": guild_id,
        "queue": get_queue(guild_id)
    }


@app.post("/queue/{guild_id}")
async def queue_add(
    guild_id: str,
    track: dict
):
    queue = add_to_queue(guild_id, track)

    return {
        "guild_id": guild_id,
        "queue": queue
    }


@app.delete("/queue/{guild_id}")
async def queue_clear(guild_id: str):
    clear_queue(guild_id)

    return {
        "guild_id": guild_id,
        "queue": []
    }


@app.delete("/queue/{guild_id}/{index}")
async def queue_remove(
    guild_id: str,
    index: int
):
    removed = remove_from_queue(guild_id, index)

    if removed is None:
        return {
            "error": "Track not found"
        }

    return {
        "removed": removed,
        "queue": get_queue(guild_id)
    }


@app.post("/queue/{guild_id}/next")
async def queue_next(
    guild_id: str,
    session_id: str
):
    return await play_next(
        guild_id,
        session_id
    )