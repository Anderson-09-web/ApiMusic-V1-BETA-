import os
import discord
from dotenv import load_dotenv
from bot.lavalink import bot

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

@bot.event
async def on_ready():
    print(f"🤖 Conectado como {bot.user}")

    channel_id = input("ID del canal de Discord donde enviar la prueba: ").strip()

    channel = bot.get_channel(int(channel_id))

    if channel is None:
        print("❌ No encontré ese canal.")
        await bot.close()
        return

    components = [
        {
            "type": 10,
            "content": "## 🎧 Music Panel\n**Probando Components V2**"
        },
        {
            "type": 14,
            "divider": True,
            "spacing": 1
        },
        {
            "type": 10,
            "content": "🎵 **Canción de prueba**\n👤 Artista de prueba\n⏱️ `0:42 / 3:20`"
        },
        {
            "type": 14,
            "divider": True,
            "spacing": 1
        },
        {
            "type": 1,
            "components": [
                {
                    "type": 2,
                    "style": 2,
                    "label": "Anterior",
                    "emoji": {"name": "⏮️"},
                    "custom_id": "music_previous"
                },
                {
                    "type": 2,
                    "style": 2,
                    "label": "Pausa",
                    "emoji": {"name": "⏯️"},
                    "custom_id": "music_pause"
                },
                {
                    "type": 2,
                    "style": 2,
                    "label": "Siguiente",
                    "emoji": {"name": "⏭️"},
                    "custom_id": "music_next"
                }
            ]
        },
        {
            "type": 14,
            "divider": True,
            "spacing": 1
        },
        {
            "type": 1,
            "components": [
                {
                    "type": 2,
                    "style": 2,
                    "label": "Aleatorio",
                    "emoji": {"name": "🔀"},
                    "custom_id": "music_shuffle"
                },
                {
                    "type": 2,
                    "style": 2,
                    "label": "Repetir",
                    "emoji": {"name": "🔁"},
                    "custom_id": "music_loop"
                },
                {
                    "type": 2,
                    "style": 2,
                    "label": "Cola",
                    "emoji": {"name": "📋"},
                    "custom_id": "music_queue"
                },
                {
                    "type": 2,
                    "style": 2,
                    "label": "Detener",
                    "emoji": {"name": "⏹️"},
                    "custom_id": "music_stop"
                }
            ]
        }
    ]

    flags = discord.MessageFlags(components_v2=True)

    try:
        await channel.send(
            components=components,
            flags=flags
        )
        print("✅ Panel V2 enviado correctamente.")
    except Exception as e:
        print(f"❌ Error enviando Components V2: {type(e).__name__}: {e}")

    await bot.close()


bot.run(TOKEN)
