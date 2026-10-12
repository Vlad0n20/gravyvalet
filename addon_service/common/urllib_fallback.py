"""fallback http sending for providers whose CDN challenges aiohttp requests

Some providers (e.g. Mendeley, behind Cloudflare) answer aiohttp requests with a
"403 text/html" bot challenge, though the same request sent with stdlib `urllib` gets through.
"""

import asyncio
import dataclasses
import json
import urllib.error
import urllib.parse
import urllib.request
from http import HTTPStatus
from typing import (
    Any,
    Iterable,
)


__all__ = ("BufferedResponse", "is_bot_challenge", "send")

USER_AGENT = "GravyValet/1.0"
_TIMEOUT_SECONDS = 30


@dataclasses.dataclass
class BufferedResponse:
    status: int
    content_type: str
    headers: list[tuple[str, str]]
    body: bytes
    charset: str = "utf-8"

    @property
    def text(self) -> str:
        return self.body.decode(self.charset)

    def json(self) -> Any:
        return json.loads(self.text)


def is_bot_challenge(status: int, content_type: str | None) -> bool:
    return status == HTTPStatus.FORBIDDEN and content_type == "text/html"


async def send(
    method: str,
    url: str,
    *,
    headers: Iterable[tuple[str, str]] = (),
    params: Iterable[tuple[str, str]] | None = None,
    json_body: Any = None,
    data: str | bytes | dict | None = None,
) -> BufferedResponse:
    return await asyncio.to_thread(
        _send_blocking, str(method), url, headers, params, json_body, data
    )


def _send_blocking(method, url, headers, params, json_body, data) -> BufferedResponse:
    _headers = dict(headers)
    _headers["User-Agent"] = USER_AGENT
    _body = None
    if json_body is not None:
        _body = json.dumps(json_body).encode()
        _headers.setdefault("Content-Type", "application/json")
    elif isinstance(data, dict):
        _body = urllib.parse.urlencode(data).encode()
        _headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
    elif isinstance(data, str):
        _body = data.encode()
    elif data is not None:
        _body = data
    if params:
        _sep = "&" if urllib.parse.urlsplit(url).query else "?"
        url = f"{url}{_sep}{urllib.parse.urlencode(list(params))}"
    _request = urllib.request.Request(url, data=_body, method=method, headers=_headers)
    try:
        with urllib.request.urlopen(_request, timeout=_TIMEOUT_SECONDS) as _response:
            return _buffer(_response, _response.status)
    except urllib.error.HTTPError as _error:
        return _buffer(_error, _error.code)


def _buffer(response, status: int) -> BufferedResponse:
    return BufferedResponse(
        status=status,
        content_type=response.headers.get_content_type(),
        headers=list(response.headers.items()),
        body=response.read(),
        charset=response.headers.get_content_charset() or "utf-8",
    )
