from typing import Dict, List, Optional


queues: Dict[str, List[dict]] = {}


def get_queue(guild_id: str) -> List[dict]:
    return queues.get(guild_id, [])


def add_to_queue(guild_id: str, track: dict):
    if guild_id not in queues:
        queues[guild_id] = []

    queues[guild_id].append(track)

    return queues[guild_id]


def pop_next(guild_id: str) -> Optional[dict]:
    if guild_id not in queues:
        return None

    if not queues[guild_id]:
        return None

    return queues[guild_id].pop(0)


def clear_queue(guild_id: str):
    queues.pop(guild_id, None)

    return []


def remove_from_queue(guild_id: str, index: int):
    if guild_id not in queues:
        return None

    if index < 0 or index >= len(queues[guild_id]):
        return None

    return queues[guild_id].pop(index)
