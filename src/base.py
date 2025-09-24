from dataclasses import dataclass
from typing import Optional, List

STOP_TOKEN = "<|endoftext|>"

@dataclass(frozen=True)
class Message:
    user: str
    text: Optional[str] = None

    def render(self):
        result = self.user + ":"
        if self.text is not None:
            result += " " + self.text
        return result

@dataclass
class Conversation:
    messages: List[Message]

    def prepend(self, message: Message):
        self.messages.insert(0, message)
        return self

    def render(self):
        return f"\n".join(
            [message.render() for message in self.messages]
        )

    def stop_tokens(self, additional = []):
        return list(dict.fromkeys([STOP_TOKEN] + [message.user + ":" for message in self.messages] + additional))

@dataclass(frozen=True)
class Config:
    name: str
    instructions: str
    example_conversations: List[Conversation]

@dataclass(frozen=True)
class Prompt:
    header: str
    examples: List[Conversation]
    convo: Conversation

    def render(self):
        if self.examples:
            return self.header + "\n\n\nExample conversations:\n" + f"\n".join([conversation.render() for conversation in self.examples]) + "\n\n\nCurrent conversation:\n" + self.convo.render(),
        else:
            return self.header + "\n\n\n" + self.convo.render()
