def __get_token():
    try:
        return open("token.txt", "r", encoding="utf-8").read()
    except:
        open("token.txt", "w", encoding="utf-8").write("")
        raise Exception("token.txt is empty. Please add your discord token.")


YOUTUBE_EMOJI = "<:yt:1100476101257601035>"
SOUNDCLOUD_EMOJI = "<:sc:1138784426776596520>"
DEEZER_EMOJI = "<:dz:1138785032618647583>"

INVITE = "https://discord.com/"
SUPPORT_SERVER = "https://discord.gg/"

TOKEN = __get_token()
