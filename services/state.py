from typing import Dict


players: Dict[str, dict] = {}


def default_state(guild_id: str) -> dict:
    return {
        "guild_id": guild_id,
        "track": None,
        "playing": False,
        "paused": False,
        "position": 0,
        "volume": 100
    }


def get_state(guild_id: str) -> dict:
    if guild_id not in players:
        return default_state(guild_id)

    return players[guild_id]


def update_state(
    guild_id: str,
    **values
) -> dict:
    if guild_id not in players:
        players[guild_id] = default_state(guild_id)

    players[guild_id].update(values)

    return players[guild_id]


def clear_state(guild_id: str):
    players.pop(guild_id, None)

    return default_state(guild_id)