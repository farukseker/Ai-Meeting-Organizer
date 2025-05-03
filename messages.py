from langchain_core.messages import BaseMessage
from typing import Literal


class MeetingMessage(BaseMessage):
    type: Literal["system"] = "meeting"
