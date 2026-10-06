import os
import discord
from dotenv import load_dotenv
from bot.lavalink import bot

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")


class MusicPanel(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

        # Texto V2
        self.add_item(
            discord.ui.TextDisplay(
                content="🎵 **Music Panel V2**\nControles de reproducción"
            )
        )

        # Separador V2
        self.add_item(
            discord.ui.Separator()
        )

        # Fila de botones
        row = discord.ui.ActionRow()

        row.add_item(
            discord.ui.Button(
                label="⏮️",
                style=discord.ButtonStyle.secondary,
                custom_id="music_previous"
            )
        )

        row.add_item(
            discord.ui.Button(
                label="⏯️",
                style=discord.ButtonStyle.primary,
                custom_id="music_pause"
            )
        )

        row.add_item(
            discord.ui.Button(
                label="⏭️",
                style=discord.ButtonStyle.secondary,
                custom_id="music_next"
            )
        )

        self.add_item(row)

        # Otro separador
        self.add_item(
            discord.ui.Separator()
        )

        # Información inferior
        self.add_item(
            discord.ui.TextDisplay(
                content="🔊 Volumen: **100%**  •  📋 Cola: **0**"
            )
        )


@bot.event
async def on_ready():
    print(f"🤖 Conectado como {bot.user}")

    channel_id = input(
        "ID del canal de Discord donde enviar la prueba: "
    ).strip()

    channel = bot.get_channel(int(channel_id))

    if channel is None:
        print("❌ No encontré ese canal.")
        await bot.close()
        return

    try:
        view = MusicPanel()

        print("\n=== COMPONENTES GENERADOS ===")
        print(view.to_components())

        message = await channel.send(
            view=view
        )

        print(f"\n✅ Panel V2 enviado correctamente.")
        print(f"🆔 Mensaje: {message.id}")

    except Exception as e:
        print(
            f"❌ Error: {type(e).__name__}: {e}"
        )

    await bot.close()


bot.run(TOKEN)
