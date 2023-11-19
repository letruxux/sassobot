import discord
from discord.ext import commands
from discord.utils import get


class Checks:
    def __init__(self, bot: discord.Client | commands.Bot) -> None:
        self.bot = bot
        pass

    def join(self, ctx: commands.Context, *args):
        if ctx.voice_client:
            if len(ctx.guild.me.voice.channel.members) == 1:
                return True
            else:
                return f"Sono già in un canale vocale!"
        if not ctx.author.voice:
            return f"Non sei in un canale vocale!"
        return True

    def play(self, ctx: commands.Context, *args):
        if not ctx.author.voice:
            return f"Non sei in un canale vocale!"
        if ctx.voice_client:
            if ctx.voice_client.is_playing():
                return f"Sto già riproducendo qualcos'altro!"
        return True

    def stop(self, ctx: commands.Context, *args):
        if not ctx.voice_client:
            return f"Non sono in un canale vocale!"
        if not ctx.author.voice:
            return f"Non sei in un canale vocale!"
        if not ctx.voice_client.is_playing():
            return f"Non sto riproducendo niente!"
        return True

    def leave(self, ctx: commands.Context, *args):
        if not ctx.voice_client:
            return f"Non sono in un canale vocale!"
        if not ctx.author.voice:
            return f"Non sei in un canale vocale!"
        if ctx.voice_client.channel != ctx.author.voice.channel:
            return f"Non siamo nello stesso canale vocale!"
        return True
