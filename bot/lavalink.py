import discord
from discord.ext import commands


class MusicBot(commands.Bot):
    async def setup_hook(self):
        pass


intents = discord.Intents.default()
intents.message_content = True

bot = MusicBot(
    command_prefix="!",
    intents=intents
)
