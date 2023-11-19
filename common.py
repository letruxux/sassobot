import discord
from typing import Any, Dict, List
from datetime import datetime
from discord import Color as c
from enum import Enum
from urllib.parse import urlparse
from json import dump


class Platform:
    def __init__(self, name: str, emoji: str, base_url: str) -> None:
        self.name = name
        self.emoji = emoji
        self.base_url = base_url
        pass


class platforms:
    Unknown = Platform("Unknown", ":question:", "")
    YouTube = Platform("YouTube", "<:yt:1100476101257601035>", "https://youtu.be/")
    Soundcloud = Platform(
        "Soundcloud", "<:sc:1138784426776596520>", "https://soundcloud.com/"
    )
    Deezer = Platform("Deezer", "<:dz:1138785032618647583>", "https://deezer.com/")


def getPlatform(url: str) -> Platform:
    parsed = urlparse(url)
    if parsed.hostname.endswith("youtu.be") or parsed.hostname.endswith("youtube.com"):
        return platforms.YouTube
    if parsed.hostname.endswith("deezer.page.link") or parsed.hostname.endswith(
        "deezer.com"
    ):
        pass  # return platforms.Deezer
    if parsed.hostname.endswith("soundcloud.com"):
        return platforms.Soundcloud
    return platforms.Unknown


class basicVideoInfo:
    def __init__(self, url: str, info: Dict, source) -> None:
        with open("porcazo.json", "w", encoding="utf-8") as f:
            dump(info, f)
        self.url: str = url
        self.platform: Platform = getPlatform(url)
        self.title: str = info.get("title")
        self.id: str = info.get("id")

        try:
            if self.platform == platforms.YouTube:
                self.thumb_url: str = (
                    f"https://img.youtube.com/vi/{self.id}/maxresdefault.jpg"
                )
            elif self.platform == platforms.Deezer:
                self.thumb_url: str = info["thumbnails"][0]["url"]
            elif self.platform == platforms.Soundcloud:
                self.thumb_url: str = info["thumbnails"][len(info["thumbnails"]) - 1][
                    "url"
                ]
        except:
            self.thumb_url: str = ""

        try:
            if self.platform == platforms.YouTube:
                self.duration: int = round(
                    info.get("formats")[0].get("fragments")[0].get("duration")
                )
            elif self.platform == platforms.Soundcloud:
                self.duration: int = round(info.get("duration"))
            else:
                self.duration: int = 0
        except:
            self.duration: int = 0

        self.extracted_info: Dict = info
        self.source: function = source
        pass


class serverSession:
    def __init__(self, guild: discord.Guild, bot) -> None:
        self.current: basicVideoInfo = None
        self.queue: List[basicVideoInfo] = []
        self.guild_id = guild.id
        self.bot = bot
        self.looping = False
        pass

    async def addToQueue(self, url):
        from ytdl import YTDLSource

        resolved = await YTDLSource.from_url(url, loop=self.bot.loop)
        source = resolved[0]
        info = resolved[1]
        result = basicVideoInfo(info=info, source=source, url=url, name=info["title"])
        self.queue.append(result)
        return result


def addots(testo, lunghezza):
    return testo[: lunghezza - 3] + "..." if lunghezza < len(testo) else testo


class dEmbed(discord.Embed):
    def __init__(
        self,
        *,
        colour: int | discord.colour.Colour | None = None,
        color: int | discord.colour.Colour | None = c.random(),
        title: Any | None = None,
        type="rich",
        url: Any | None = None,
        description: Any | None = None,
        timestamp: datetime | None = datetime.now(),
    ):
        super().__init__(
            colour=colour,
            color=color,
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=timestamp,
        )
        try:
            super().set_footer(
                text=f"developed by @letruxux",
            )
        except:
            pass

    def set_footer(
        self, *, text: Any | None = None, icon_url: Any | None = None
    ) -> None:
        return super().set_footer(
            text=f"{text} | developed by @letruxux", icon_url=icon_url
        )


class emojis:
    yt = "<:yt:1100476101257601035>"
