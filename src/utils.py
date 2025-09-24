from src.constants import (
    ALLOWED_SERVER_IDS,
)
import logging

logger = logging.getLogger(__name__)
from src.base import Message
from discord import Message as DiscordMessage
from typing import Optional, List
import discord

from src.constants import MAX_CHARS_PER_REPLY_MSG, INACTIVATE_THREAD_PREFIX

def discord_message_to_message(message: DiscordMessage, bot_user) -> list[Message]:
    if message.author == bot_user:
        split=message.content.partition(":")
        if len(split) == 3:
            return [Message(user=split[0], text=split[2].partition('\n')[0].strip())]
        else:
            return []
    if bot_user in message.mentions:
        return []
    if message.content:
        return [
            Message(user=message.author.name, text=content)
            for content in message.clean_content.splitlines()
        ]
    return []

def is_last_message_stale(
    interaction_message: DiscordMessage, last_message: DiscordMessage, bot_id: str
) -> bool:
    return (
        last_message
        and last_message.id != interaction_message.id
        and last_message.author
        and last_message.author.id != bot_id
    )

async def close_thread(thread: discord.Thread):
    await thread.edit(name=INACTIVATE_THREAD_PREFIX)
    await thread.send(
        embed=discord.Embed(
            description="**Thread closed** - Context limit reached, closing...",
            color=discord.Color.blue(),
        )
    )
    await thread.edit(archived=True, locked=True)


def should_block(guild: Optional[discord.Guild]) -> bool:
    if guild is None:
        # dm's not supported
        logger.info(f"DM not supported")
        return True

    if guild.id and guild.id not in ALLOWED_SERVER_IDS:
        # not allowed in this server
        logger.info(f"Guild {guild} not allowed")
        return True
    return False
