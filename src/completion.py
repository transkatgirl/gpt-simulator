from enum import Enum
from dataclasses import dataclass
import openai
from typing import Optional, List
from src.constants import (
    #BOT_INSTRUCTIONS,
    #BOT_NAME,
    #EXAMPLE_CONVOS,
    MODEL,
    OPENAI_API_BASE
)
import discord
from src.base import Message, Prompt, Conversation, STOP_TOKENS
from src.utils import close_thread, logger

#MY_BOT_NAME = BOT_NAME
#MY_BOT_EXAMPLE_CONVOS = EXAMPLE_CONVOS

class CompletionResult(Enum):
    OK = 0
    INVALID_REQUEST = 1
    OTHER_ERROR = 2


@dataclass
class CompletionData:
    status: CompletionResult
    reply_text: Optional[str]
    status_text: Optional[str]


async def generate_completion_response(
    messages: List[Message], user: Optional[str]
) -> CompletionData:
    try:
        openai.api_base = OPENAI_API_BASE
        openai.api_type = "openai"
        #prompt = Prompt(
        #    header=Message(
        #        "System", f"Instructions for {MY_BOT_NAME}: {BOT_INSTRUCTIONS}"
        #    ),
        #    examples=MY_BOT_EXAMPLE_CONVOS,
        #    convo=Conversation(messages + [Message(MY_BOT_NAME)]),
        #)
        #conversation = Conversation(messages + [Message(MY_BOT_NAME)])
        conversation = Conversation(messages + [Message(user)]) if user else Conversation(messages)
        rendered_conversation = conversation.render()
        if not user:
            rendered_conversation += "\n"
        stop_tokens = conversation.stop_tokens([user]) if user else STOP_TOKENS
        print("\n---\n\n# Prompt\n\n" + rendered_conversation)
        print("\n# Stop Tokens\n")
        print(stop_tokens)
        print("\n---\n")
        response = openai.Completion.create(
            model=MODEL,
            prompt=rendered_conversation,
            temperature=1.0,
            top_p=0.95,
            max_tokens=512,
            stop=stop_tokens,
        )
        reply = response.choices[0].text.strip()
        return CompletionData(
            status=CompletionResult.OK, reply_text=reply, status_text=None
        )
    except openai.error.InvalidRequestError as e:
        logger.exception(e)
        return CompletionData(
            status=CompletionResult.INVALID_REQUEST,
            reply_text=None,
            status_text=str(e),
        )
    except Exception as e:
        logger.exception(e)
        return CompletionData(
            status=CompletionResult.OTHER_ERROR, reply_text=None, status_text=str(e)
        )


async def process_response(
    user: Optional[str], thread: discord.Thread, response_data: CompletionData
):
    status = response_data.status
    reply_text = response_data.reply_text
    status_text = response_data.status_text
    if status is CompletionResult.OK:
        sent_message = None
        if not reply_text:
            sent_message = await thread.send(
                embed=discord.Embed(
                    description=f"**Invalid response** - empty response",
                    color=discord.Color.yellow(),
                )
            )
        else:
            #if not user and ':' not in reply_text:
            #    print("\n---\n\n# Response [Failed]\n\n" + reply_text)
            #    print("\n---\n\n")
            #    sent_message = await thread.send(
            #        embed=discord.Embed(
            #            description=f"**Invalid response** - no username delimiter",
            #            color=discord.Color.yellow(),
            #        )
            #    )
            #else:
            message = Message(user, reply_text).render() if user else reply_text
            print("\n---\n\n# Response\n\n" + message)
            print("\n---\n\n")
            sent_message = await thread.send(message)
    elif status is CompletionResult.INVALID_REQUEST:
        await thread.send(
            embed=discord.Embed(
                description=f"**Invalid request** - {status_text}",
                color=discord.Color.yellow(),
            )
        )
    else:
        await thread.send(
            embed=discord.Embed(
                description=f"**Error** - {status_text}",
                color=discord.Color.yellow(),
            )
        )
