import os

import aiohttp
import discord
import wavelink
from dotenv import load_dotenv

from bot.lavalink import bot
from services.queue import add_to_queue, get_queue, pop_next, clear_queue
from bot.music_panel import MusicPanel, loop_modes


load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("Falta DISCORD_TOKEN en el archivo .env")

music_panel_messages = {}


async def send_or_update_music_panel(channel, player):
    guild_id = player.guild.id
    message = music_panel_messages.get(guild_id)
    view = MusicPanel(player)

    if message is not None:
        try:
            await message.edit(view=view)
            return message
        except discord.HTTPException:
            music_panel_messages.pop(guild_id, None)

    message = await channel.send(view=view)
    music_panel_messages[guild_id] = message
    return message


async def refresh_music_panel(player):
    message = music_panel_messages.get(player.guild.id)
    if message is None:
        return
    try:
        await message.edit(view=MusicPanel(player))
    except discord.HTTPException as e:
        print(f"Error actualizando panel: {e}")



@bot.event
async def on_ready():
    print(f"🤖 Bot conectado: {bot.user}")
    print(f"🆔 ID: {bot.user.id}")

    if not wavelink.Pool.nodes:
        node = wavelink.Node(
            identifier="local",
            uri=os.getenv("LAVALINK_URI", "http://127.0.0.1:8080"),
            password=os.getenv("LAVALINK_PASSWORD", "musicapi"),
            client=bot
        )

        await wavelink.Pool.connect(
            nodes=[node],
            client=bot
        )

        print("🎧 Lavalink conectado")


async def music_api_search(query: str):
    url = os.getenv("MUSIC_API_URL", "http://127.0.0.1:8000") + "/search"

    async with aiohttp.ClientSession() as session:
        async with session.get(
            url,
            params={"query": query}
        ) as response:

            data = await response.json()

            if response.status != 200:
                raise RuntimeError(
                    f"Music API respondió {response.status}"
                )

            return data


async def play_next_from_queue(player: wavelink.Player):
    guild_id = str(player.guild.id)

    next_item = pop_next(guild_id)

    if next_item is None:
        print(f"📋 Cola vacía en {guild_id}")
        return False

    track = next_item.get("track")

    if track is None:
        print("❌ La siguiente pista no tiene track.")
        return False

    await player.play(track)

    print(
        f"▶️ Siguiente: "
        f"{track.title} - {track.author}"
    )

    return True


@bot.event
async def on_wavelink_track_end(
    payload: wavelink.TrackEndEventPayload
):
    player = payload.player

    if not isinstance(player, wavelink.Player):
        return

    print(
        f"🏁 Track terminó: "
        f"{payload.track.title} | razón: {payload.reason}"
    )

    if payload.reason != "finished":
        return

    guild_id = str(player.guild.id)

    if loop_modes.get(guild_id, False):
        await player.play(payload.track)
        await refresh_music_panel(player)
        return

    started = await play_next_from_queue(player)
    if started:
        await refresh_music_panel(player)


@bot.command()
async def api_search(ctx, *, query: str):
    try:
        data = await music_api_search(query)
        results = data.get("results", [])

        if not results:
            await ctx.send("❌ No encontré resultados.")
            return

        track = results[0]

        await ctx.send(
            f"🎵 **{track['title']}**\n"
            f"👤 {track['author']}\n"
            f"⏱️ {track['duration']} ms\n"
            f"🆔 `{track['identifier']}`"
        )

    except Exception as e:
        print(f"❌ Error Music API: {e}")
        await ctx.send("❌ No pude conectar con la Music API.")


@bot.command()
async def play(ctx, *, query: str):
    try:
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("❌ Primero entra a un canal de voz.")
            return

        channel = ctx.author.voice.channel

        data = await music_api_search(query)
        results = data.get("results", [])

        if not results:
            await ctx.send("❌ No encontré esa canción.")
            return

        track_data = results[0]
        identifier = track_data.get("identifier")

        if not identifier:
            await ctx.send(
                "❌ La API no devolvió un identificador válido."
            )
            return

        player = ctx.voice_client

        if not isinstance(player, wavelink.Player):
            player = await channel.connect(cls=wavelink.Player)

        tracks = await wavelink.Pool.fetch_tracks(
            f"https://www.youtube.com/watch?v={identifier}"
        )

        if not tracks:
            await ctx.send(
                "❌ Lavalink no pudo cargar la pista."
            )
            return

        track = tracks[0]
        guild_id = str(ctx.guild.id)

        # Si ya hay una canción reproduciéndose o pausada,
        # la nueva canción entra a la cola.
        if player.current is not None:
            add_to_queue(
                guild_id,
                {
                    "track": track,
                    "title": track.title,
                    "author": track.author
                }
            )

            position = len(get_queue(guild_id))

            await send_or_update_music_panel(ctx.channel, player)

            await ctx.send(
                f"📋 Añadida a la cola: **{track.title}** "
                f"(posición {position})."
            )

            print(
                f"📋 Cola +1: "
                f"{track.title} - {track.author}"
            )

            return

        await player.play(track)

        await send_or_update_music_panel(ctx.channel, player)

        print(
            f"▶️ Reproduciendo: "
            f"{track.title}"
        )

    except Exception as e:
        print(f"❌ Error en -play: {e}")
        await ctx.send(
            f"❌ Error: `{type(e).__name__}`"
        )


@bot.command()
async def nowplaying(ctx):
    try:
        player = ctx.voice_client

        if not isinstance(player, wavelink.Player):
            await ctx.send("❌ No estoy conectado a un canal de voz.")
            return

        track = player.current

        if track is None:
            await ctx.send("❌ No hay ninguna canción reproduciéndose.")
            return

        position = getattr(player, "position", 0) or 0
        duration = getattr(track, "length", 0) or 0

        def format_time(ms):
            total_seconds = max(0, int(ms / 1000))
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}:{seconds:02d}"

        current_time = format_time(position)
        total_time = format_time(duration)

        queued = len(get_queue(str(ctx.guild.id)))

        embed = discord.Embed(
            title="🎧 Ahora reproduciendo",
            description=(
                f"**{track.title}**\n"
                f"👤 {track.author}"
            ),
        )

        embed.add_field(
            name="⏱️ Progreso",
            value=f"`{current_time} / {total_time}`",
            inline=True
        )

        embed.add_field(
            name="📋 En cola",
            value=f"`{queued}` canción(es)",
            inline=True
        )

        await ctx.send(embed=embed)

    except Exception as e:
        print(f"❌ Error en -nowplaying: {e}")
        await ctx.send(
            f"❌ Error: `{type(e).__name__}`"
        )


@bot.command()
async def queue(ctx):
    guild_id = str(ctx.guild.id)
    tracks = get_queue(guild_id)

    if not tracks:
        await ctx.send("📋 La cola está vacía.")
        return

    lines = []

    for index, item in enumerate(tracks, start=1):
        title = item.get("title", "Desconocida")
        author = item.get("author", "Desconocido")

        lines.append(
            f"**{index}.** 🎵 {title} • {author}"
        )

    await ctx.send(
        "📋 **Cola de reproducción**\n\n"
        + "\n".join(lines)
    )


@bot.command()
async def volume(ctx, amount: int = None):
    try:
        player = ctx.voice_client

        if not isinstance(player, wavelink.Player):
            await ctx.send("❌ No estoy conectado a un canal de voz.")
            return

        current_volume = getattr(player, "volume", 100)

        if amount is None:
            embed = discord.Embed(
                title="🔊 Volumen",
                description=f"El volumen actual es **{current_volume}%**.",
            )
            await ctx.send(embed=embed)
            return

        if amount < 0 or amount > 100:
            await ctx.send("❌ El volumen debe estar entre **0 y 100**.")
            return

        await player.set_volume(amount)

        embed = discord.Embed(
            title="🔊 Volumen actualizado",
            description=f"Volumen establecido en **{amount}%**.",
        )
        await ctx.send(embed=embed)

    except Exception as e:
        print(f"❌ Error en -volume: {e}")
        await ctx.send(
            f"❌ Error: `{type(e).__name__}`"
        )


@bot.command()
async def pause(ctx):
    try:
        player = ctx.voice_client

        if not isinstance(player, wavelink.Player):
            await ctx.send(
                "❌ No estoy reproduciendo música."
            )
            return

        if not player.playing:
            await ctx.send(
                "⏸️ La música ya está pausada."
            )
            return

        await player.pause(True)
        await ctx.send("⏸️ Música pausada.")

    except Exception as e:
        print(f"❌ Error en -pause: {e}")
        await ctx.send(
            f"❌ Error: `{type(e).__name__}`"
        )


@bot.command()
async def resume(ctx):
    try:
        player = ctx.voice_client

        if not isinstance(player, wavelink.Player):
            await ctx.send(
                "❌ No estoy reproduciendo música."
            )
            return

        if not player.paused:
            await ctx.send(
                "▶️ La música ya está reproduciéndose."
            )
            return

        await player.pause(False)
        await ctx.send("▶️ Música reanudada.")

    except Exception as e:
        print(f"❌ Error en -resume: {e}")
        await ctx.send(
            f"❌ Error: `{type(e).__name__}`"
        )


@bot.command()
async def skip(ctx):
    try:
        player = ctx.voice_client

        if not isinstance(player, wavelink.Player):
            await ctx.send(
                "❌ No estoy reproduciendo música."
            )
            return

        if player.current is None:
            await ctx.send(
                "❌ No hay ninguna canción reproduciéndose."
            )
            return

        next_item = pop_next(str(ctx.guild.id))

        if next_item is None:
            await player.stop()
            await ctx.send(
                "⏭️ Canción saltada. No hay más canciones."
            )
            return

        next_track = next_item.get("track")

        if next_track is None:
            await player.stop()
            await ctx.send(
                "❌ La siguiente canción no es válida."
            )
            return

        await player.play(next_track)

        await ctx.send(
            f"⏭️ **Saltada**\n"
            f"▶️ Ahora: **{next_track.title}**"
        )

        print(
            f"⏭️ Skip → "
            f"{next_track.title}"
        )

    except Exception as e:
        print(f"❌ Error en -skip: {e}")
        await ctx.send(
            f"❌ Error: `{type(e).__name__}`"
        )


@bot.command()
async def stop(ctx):
    try:
        player = ctx.voice_client

        if not isinstance(player, wavelink.Player):
            await ctx.send(
                "❌ No estoy en un canal de voz."
            )
            return

        clear_queue(str(ctx.guild.id))

        await player.stop()

        await ctx.send(
            "⏹️ Música detenida y cola limpiada."
        )

    except Exception as e:
        print(f"❌ Error en -stop: {e}")
        await ctx.send(
            f"❌ Error: `{type(e).__name__}`"
        )


bot.run(TOKEN)
