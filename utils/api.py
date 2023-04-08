import json
import re
from typing import Dict, Generator, List, Optional, Union
from urllib.parse import urljoin
from .typings import *

import requests


class V1:
    BASE_URL = "https://api.openai.com/"
    MODEL = "gpt-3.5-turbo"
    TIMEOUT = 360

    def __init__(
        self,
        key: str,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        timeout: Optional[int] = None,
    ) -> None:
        self.key = f"Bearer {key}"
        self.base_url = base_url or self.BASE_URL
        self.model = model or self.MODEL
        self.temperature = temperature or 1
        self.top_p = top_p or 1
        self.timeout = timeout or self.TIMEOUT
        self.messages: List[Dict[str, str]] = []
        self.session = requests.Session()
        self.session.headers.update({"Authorization": self.key})

    def add_message(self, message: Union[str, Dict[str, str]], role: str = "user") -> None:
        if isinstance(message, str):
            message = {"content": message, "role": role}
        self.messages.append(message)

    def ask(
        self,
        prompt: str,
        user: Optional[str] = None,
        stream: bool = False,
        n: int = 1,
    ) -> Union[Generator[AskResponse, None, None], List[AskResponse]]:
        self.add_message(prompt)

        data = {
            "model": self.model,
            "messages": self.messages,
            "stream": stream,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "n": n,
            "user": user or "chatgpt-python",
        }

        url = urljoin(self.base_url, "/v1/chat/completions")

        response = self.session.post(
            url,
            json=data,
            stream=stream,
            timeout=self.timeout,
        )
        response.raise_for_status()

        if stream:
            return self._stream_response(response)

        return self._single_response(response)

    def _stream_response(
        self, response: requests.Response
    ) -> Generator[StreamAskResponse, None, None]:
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue

            data = self._format_stream_message(line)
            if not self._check_stream_fields(data):
                continue

            answer = data["choices"][0]["delta"]["content"]
            message_id = data["id"]

            self.add_message(answer, "assistant")

            yield StreamAskResponse(answer, message_id, self.model)

    def _single_response(self, response: requests.Response) -> List[AskResponse]:
        data = response.json()

        if not self._check_fields(data):
            raise ValueError("Field missing")

        answer = data["choices"][0]["text"]
        self.add_message(answer, "assistant")

        return [
            AskResponse(
                answer=answer,
                id=data["id"],
                model=self.model,
                usage=data["model"]["usage"],
            )
        ]

    def _check_fields(self, data: Dict[str, Union[str, Dict[str, str]]]) -> bool:
        return (
            "choices" in data
            and len(data["choices"]) > 0
            and "text" in data["choices"][0]
            and "id" in data
            and "model" in data
        )

    def _check_stream_fields(self, data: Dict[str, Union[str, Dict[str, str]]]) -> bool:
        return (
            "choices" in data
            and len(data["choices"]) > 0
            and "delta" in data["choices"][0]
            and "content" in data["choices"][0]["delta"]
            and "id" in data
        )

    def _format_stream_message(self, line: str) -> Dict[str, Union[str, Dict[str, str]]]:
        matches = re.match(r"data: (.+)", line)
        if not matches:
            return {}

        data = json.loads(matches.group(1))
        if not self._check_stream_fields(data):
            return {}

        return data
