from typing import Dict, Generator, List, Optional


class Message:
    def __init__(self, content: str, role: str = "user") -> None:
        self.content = content
        self.role = role

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


class AskResponse:
    def __init__(self, answer: str, id: str, model: str, usage: Dict[str, int]) -> None:
        self.answer = answer
        self.id = id
        self.model = model
        self.usage = usage


class StreamAskResponse:
    def __init__(self, answer: str, id: str, model: str) -> None:
        self.answer = answer
        self.id = id
        self.model = model
