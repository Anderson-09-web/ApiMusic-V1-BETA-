import random
import discord

from services.queue import get_queue, pop_next, clear_queue


loop_modes = {}


class MusicPanel(discord.ui.LayoutView):

    def __init__(self, player):
        super().__init__(timeout=None)

        self.player = player
        self.guild_id = str(player.guild.id)

        track = player.current
        title = getattr(track, "title", "Nada reproduciéndose")
        author = getattr(track, "author", "Desconocido")
        volume = getattr(player, "volume", 100)
        queued = len(get_queue(self.guild_id))
        paused = player.paused
        loop = loop_modes.get(self.guild_id, False)

        self.add_item(
            discord.ui.TextDisplay(
                content=(
                    "# 🎧 MUSIC PLAYER\n"
                    "━━━━━━━━━━━━━━━━━━\n"
                    f"### 🎵 {title}\n"
                    f"👤 **Artista:** {author}\n"
                    f"🔊 **Volumen:** {volume}%\n"
                    f"📋 **En cola:** {queued}\n"
                    f"🔁 **Repetición:** "
                    f"{'Activada' if loop else 'Desactivada'}"
                )
            )
        )

        self.add_item(discord.ui.Separator())

        self.row1 = discord.ui.ActionRow()

        self.previous_button = discord.ui.Button(
            label="Anterior",
            emoji="⏮️",
            style=discord.ButtonStyle.secondary,
            custom_id="music_previous",
        )
        self.previous_button.callback = self.previous
        self.row1.add_item(self.previous_button)

        self.pause_button = discord.ui.Button(
            label="Reanudar" if paused else "Pausa",
            emoji="▶️" if paused else "⏸️",
            style=discord.ButtonStyle.primary,
            custom_id="music_pause",
        )
        self.pause_button.callback = self.pause_resume
        self.row1.add_item(self.pause_button)

        self.next_button = discord.ui.Button(
            label="Siguiente",
            emoji="⏭️",
            style=discord.ButtonStyle.secondary,
            custom_id="music_next",
        )
        self.next_button.callback = self.next
        self.row1.add_item(self.next_button)

        self.add_item(self.row1)
        self.add_item(discord.ui.Separator())

        self.row2 = discord.ui.ActionRow()

        self.shuffle_button = discord.ui.Button(
            label="Aleatorio",
            emoji="🔀",
            style=discord.ButtonStyle.secondary,
            custom_id="music_shuffle",
        )
        self.shuffle_button.callback = self.shuffle
        self.row2.add_item(self.shuffle_button)

        self.loop_button = discord.ui.Button(
            label="Repetir: ON" if loop else "Repetir: OFF",
            emoji="🔁",
            style=discord.ButtonStyle.success if loop
            else discord.ButtonStyle.secondary,
            custom_id="music_loop",
        )
        self.loop_button.callback = self.toggle_loop
        self.row2.add_item(self.loop_button)

        self.volume_button = discord.ui.Button(
            label="Volumen",
            emoji="🔊",
            style=discord.ButtonStyle.secondary,
            custom_id="music_volume",
        )
        self.volume_button.callback = self.change_volume
        self.row2.add_item(self.volume_button)

        self.queue_button = discord.ui.Button(
            label="Cola",
            emoji="📋",
            style=discord.ButtonStyle.secondary,
            custom_id="music_queue",
        )
        self.queue_button.callback = self.show_queue
        self.row2.add_item(self.queue_button)

        self.stop_button = discord.ui.Button(
            label="Detener",
            emoji="⏹️",
            style=discord.ButtonStyle.danger,
            custom_id="music_stop",
        )
        self.stop_button.callback = self.stop
        self.row2.add_item(self.stop_button)

        self.add_item(self.row2)

    async def refresh(self, interaction):
        await interaction.response.edit_message(
            view=MusicPanel(self.player)
        )

    async def previous(self, interaction):
        if self.player.current is None:
            await interaction.response.send_message(
                "❌ No hay ninguna canción reproduciéndose.",
                ephemeral=True,
            )
            return

        await self.player.play(self.player.current)
        await interaction.response.send_message(
            "⏮️ Volviendo a empezar la canción actual.",
            ephemeral=True,
        )

    async def pause_resume(self, interaction):
        if self.player.current is None:
            await interaction.response.send_message(
                "❌ No hay ninguna canción reproduciéndose.",
                ephemeral=True,
            )
            return

        await self.player.pause(not self.player.paused)
        await self.refresh(interaction)

    async def next(self, interaction):
        item = pop_next(self.guild_id)

        if item is None:
            await interaction.response.send_message(
                "📋 No hay más canciones en la cola.",
                ephemeral=True,
            )
            return

        track = item.get("track")

        if track is None:
            await interaction.response.send_message(
                "❌ La siguiente canción no es válida.",
                ephemeral=True,
            )
            return

        await self.player.play(track)
        await self.refresh(interaction)

    async def shuffle(self, interaction):
        tracks = get_queue(self.guild_id)

        if len(tracks) < 2:
            await interaction.response.send_message(
                "📋 Necesitas al menos dos canciones en la cola.",
                ephemeral=True,
            )
            return

        random.shuffle(tracks)
        await self.refresh(interaction)

    async def toggle_loop(self, interaction):
        loop_modes[self.guild_id] = not loop_modes.get(
            self.guild_id, False
        )
        await self.refresh(interaction)

    async def change_volume(self, interaction):
        current = getattr(self.player, "volume", 100)
        new_volume = 25 if current >= 100 else current + 25

        await self.player.set_volume(new_volume)
        await self.refresh(interaction)

    async def show_queue(self, interaction):
        tracks = get_queue(self.guild_id)

        if not tracks:
            text = "📋 La cola está vacía."
        else:
            text = "\n".join(
                f"**{i}.** {item.get('title', 'Desconocida')}"
                for i, item in enumerate(tracks[:15], start=1)
            )

        await interaction.response.send_message(
            text[:1900],
            ephemeral=True,
        )

    async def stop(self, interaction):
        clear_queue(self.guild_id)
        loop_modes[self.guild_id] = False

        await self.player.stop()

        await interaction.response.edit_message(
            view=MusicPanel(self.player)
        )
