import os
import discord
from dotenv import load_dotenv
from bot.music_panel import MusicPanel

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = discord.Client(intents=intents)


@bot.event
async def on_ready():
    print(f"🤖 Conectado como {bot.user}")

    channel_id = int(
        input("ID del canal de Discord donde enviar la prueba: ")
    )

    channel = bot.get_channel(channel_id)

    if channel is None:
        print("❌ No encontré el canal.")
        await bot.close()
        return

    view = MusicPanel()

    message = await channel.send(view=view)

    print("✅ Panel enviado.")
    print(f"🆔 Mensaje: {message.id}")
    print("👉 Pulsa el botón ⏸️ en Discord.")

    await bot.close()


bot.run(TOKEN)
