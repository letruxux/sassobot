import discord
from yt_dlp.YoutubeDL import DownloadError
from datetime import timedelta
from discord.ext import commands
from discord import Color as c
from checks import Checks
from yt_dlp import DownloadError
from youtube_search import AsyncYoutubeSearch
from validators import url as validate
from common import addots, dEmbed, emojis, serverSession

DEV_TOKEN = ""
LIVE_TOKEN = ""
INVITE = ""
SUPPORT_SERVER = ""

sessions = {}


bot = commands.Bot(
    commands.when_mentioned_or("--"),
    help_command=None,
    intents=discord.Intents.all(),
    activity=discord.Activity(
        type=discord.ActivityType.listening, name="suoni dei sassi"
    ),
)
checks = Checks(bot)
working = False


async def devJoin(channel: discord.VoiceChannel):
    try:
        if channel.guild.voice_client:
            await channel.guild.voice_client.disconnect()
        await channel.connect()
        sessions[channel.guild.id] = serverSession(channel.guild, bot)
        return True
    except:
        return False


@bot.command(aliases=["invito", "link", "Invito", "Invite", "Link"])
async def invite(ctx: commands.Context):
    await ctx.reply(
        embed=dEmbed(
            title=f"Invita {bot.user.name} nel tuo server!",
            description=f"Puoi usare [questo]({INVITE}) link per invitare {bot.user.name} nel tuo server! Buon ascolto!",
        )
    )


@bot.command()
async def help(ctx: commands.Context):
    embed = (
        dEmbed(
            color=c.random(),
            title=f"Comandi di {bot.user.name}.",
        )
        .add_field(name="📥 join", value="Porta il bot nel tuo canale.", inline=False)
        .add_field(
            name="📤 leave", value="Fa uscire il bot dal tuo canale.", inline=False
        )
        .add_field(
            name="🔈 play [link/ricerca]",
            value="Riproduce un video da link o da ricerca.",
            inline=False,
        )
    )
    await ctx.reply(embed=embed)


@bot.command()
async def join(ctx: commands.Context):
    check = checks.join(ctx)
    if check != True:
        return await ctx.reply(check)

    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    user_channel = ctx.author.voice.channel
    if user_channel:
        await devJoin(user_channel)
        return await ctx.message.add_reaction("👍")


@bot.command()
async def leave(ctx: commands.Context):
    check = checks.leave(ctx)
    if check != True:
        return await ctx.reply(check)

    await ctx.voice_client.disconnect()
    return await ctx.message.add_reaction("👍")


@bot.command(aliases=["stoo", "stpo"])
async def stop(ctx: commands.Context):
    check = checks.stop(ctx)
    if check != True:
        return await ctx.reply(check)

    voice_client: discord.VoiceClient = discord.utils.get(
        bot.voice_clients, guild=ctx.guild
    )
    voice_client.stop()

    return await ctx.message.add_reaction("👍")


@bot.command()
async def play(ctx: commands.Context, *, prompt):
    global working
    check = checks.play(ctx)
    if check != True:
        return await ctx.reply(check)
    working = True

    await devJoin(ctx.author.voice.channel)

    color = c.random()
    is_link = validate(prompt)
    msg = await ctx.reply(
        embed=dEmbed(
            color=color,
            title=f"🔎 {'Scarico' if is_link else 'Cerco'} {f'<{addots(prompt, 20)}>' if is_link else addots(prompt, 200)}...",
        ),
    )
    if not validate(prompt):
        search = await AsyncYoutubeSearch(
            prompt, max_results=3, language="it", region="IT"
        ).fetch()
        risultati = search.list()
        if len(risultati) == 0:
            await msg.edit(
                embed=dEmbed(
                    color=c.red(),
                    title="Errore...",
                    description="Non ci sono stati risultati...",
                )
            )
            return
        view = discord.ui.View(timeout=10)
        dropdown = discord.ui.Select(min_values=1, max_values=1)
        view.add_item(dropdown)
        for risultato in risultati:
            dropdown.add_option(
                label=risultato["title"],
                description=addots(
                    f'{risultato["duration"]} | {risultato["channel"]}', 100
                ),
                value=risultato["id"],
            )
        await msg.edit(
            embed=dEmbed(
                color=color,
                title="Scegli il video che vuoi.",
                description="Se in 10 secondi non rispondi, verrà scelto il primo.",
            ),
            view=view,
        )

        async def callback(i: discord.Interaction):
            await i.response.defer()
            await i.followup.send(":thumbsup:", ephemeral=True)
            view.stop()

        dropdown.callback = callback
        if await view.wait():
            prompt = dropdown.options[0].value
        else:
            prompt = dropdown.values[0]
        prompt = "https://youtube.com/watch?v=" + prompt
    try:
        from ytdl import YTDLSource

        player = await YTDLSource.from_url(prompt, loop=bot.loop)
        if player.platform.name == "Unknown":
            return await msg.edit(
                embed=dEmbed(
                    color=c.red(),
                    title="Errore...",
                    description="Quel link non è supportato!",
                ),
                view=None,
            )
    except DownloadError:
        return await msg.edit(
            embed=dEmbed(
                color=c.red(),
                title="Errore...",
                description="Quel link non è supportato!",
            ),
            view=None,
        )

    working = False
    ctx.voice_client.play(player.source())
    return await msg.edit(
        embed=dEmbed(
            color=color,
            title="🎶 Sto riproducendo...",
            description=f"{player.platform.emoji} [**{player.title}**]({prompt})\n{f':clock1: {timedelta(seconds=player.duration)}' if player.duration != 0 else ''}",
        ).set_image(url=player.thumb_url),
        view=None,
    )


@join.error
@leave.error
@play.error
@stop.error
@help.error
async def on_error(ctx: commands.Context, err):
    errEmbed = dEmbed(title="Errore...", color=c.red())

    if isinstance(err, commands.MissingPermissions):
        owner = ctx.guild.owner
        direct_message = await owner.create_dm()
        await direct_message.send(f"Non ho abbastanza permessi in {ctx.guild.name}!")
        return

    if isinstance(err, commands.BadArgument) or isinstance(
        err, commands.errors.MissingRequiredArgument
    ):
        embed = errEmbed
        embed.description = f"{ctx.author.mention}, ti sei scordato qualche parametro?"
        await ctx.reply(embed=embed)
        return

    if isinstance(err, discord.ClientException) & (
        "already playing audio" in str(err).lower()
    ):
        embed = errEmbed
        embed.description = f"{ctx.author.mention}, c'è già qualcosa in riproduzione!"
        await ctx.reply(embed=embed)
        return

    embed = errEmbed
    embed.description = f"{ctx.author.mention}, mi dispiace ma c'è un problema inaspettato.\nSarebbe apprezzato ricevere un [report](<https://t.ly/sassoBUG>) di come riprodurre questo bug per risolverlo più in fretta!"
    await ctx.reply(embed=embed)
    raise err


@bot.event
async def on_guild_join(guild: discord.Guild):
    try:
        embed = dEmbed(
            title="Grazie per avermi aggiunto!",
            description=f"Sono appena stato aggiunto al tuo server: {guild.name}. Se ti serve aiuto, entra nel server di {bot.user.name}: {SUPPORT_SERVER}",
        )
        await bot.get_user(guild.owner_id).send(embed=embed)
    except Exception as e:
        print(e)


@bot.event
async def on_ready():
    print(f"Hey vsauce! {str(bot.user)} here.")
    print(INVITE)


bot.run(LIVE_TOKEN)
