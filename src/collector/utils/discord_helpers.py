import discord


def voice_channel_members(channel: discord.VoiceChannel) -> list[discord.Member]:
    """Return non-bot members currently in a voice channel."""
    return [m for m in channel.members if not m.bot]


def format_duration(seconds: float) -> str:
    """Format seconds as H:MM:SS or M:SS."""
    total = int(seconds)
    h, remainder = divmod(total, 3600)
    m, s = divmod(remainder, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"
