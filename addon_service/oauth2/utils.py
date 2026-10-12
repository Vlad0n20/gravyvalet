import dataclasses
import urllib.parse
from http import HTTPStatus
from secrets import token_urlsafe
from typing import Iterable

from addon_service.common import urllib_fallback
from addon_service.common.aiohttp_session import get_singleton_client_session
from addon_toolkit.iri_utils import iri_with_query


_SCOPE_DELIMITER = " "  # https://www.rfc-editor.org/rfc/rfc6749.html#section-3.3


@dataclasses.dataclass
class FreshTokenResult:
    access_token: str
    refresh_token: str | None
    expires_in: int | None
    scopes: list[str] | None

    @classmethod
    def from_token_response_json(cls, token_response_json: dict) -> "FreshTokenResult":
        """build a FreshTokenResult from a successful access token response

        see https://www.rfc-editor.org/rfc/rfc6749.html#section-5.1
        """
        return cls(
            access_token=token_response_json["access_token"],
            refresh_token=token_response_json.get("refresh_token"),
            expires_in=token_response_json.get("expires_in"),
            scopes=_parse_scope_param_value(token_response_json.get("scope")),
        )


def build_auth_url(
    *,
    auth_uri: str,
    client_id: str,
    state_token: str,
    authorized_scopes: Iterable[str] | None,
    redirect_uri: str,
) -> str:
    """build a URL that will initiate authorization when visited by a user

    see https://www.rfc-editor.org/rfc/rfc6749.html#section-4.1.1
    """
    query_params = {
        "response_type": "code",
        "client_id": client_id,
        "state": state_token,
        "redirect_uri": redirect_uri,
    }
    if authorized_scopes:
        query_params["scope"] = _SCOPE_DELIMITER.join(authorized_scopes)
    return iri_with_query(auth_uri, query_params)


def generate_state_nonce(nonce_length: int = 16):
    return token_urlsafe(nonce_length)


async def get_initial_access_token(
    *,  # keywords only
    token_endpoint_url: str,
    authorization_code: str,
    auth_callback_url: str,
    client_id: str,
    client_secret: str,
) -> FreshTokenResult:
    """get a fresh access token using a one-time authorization code

    see https://www.rfc-editor.org/rfc/rfc6749.html#section-4.1.3
    """

    return await _token_request(
        token_endpoint_url,
        {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": auth_callback_url,
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )


async def get_refreshed_access_token(
    *,  # keywords only
    token_endpoint_url: str,
    refresh_token: str,
    auth_callback_url: str,
    client_id: str,
    client_secret: str,
    scopes: Iterable[str] = (),
) -> FreshTokenResult:
    """get a fresh access token using a refresh token

    see https://www.rfc-editor.org/rfc/rfc6749.html#section-6
    """
    _refresh_params = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    if scopes:
        _refresh_params["scope"] = _SCOPE_DELIMITER.join(scopes)
    result = await _token_request(token_endpoint_url, _refresh_params)

    # If refresh token is not returned, use previous refresh token
    if not result.refresh_token:
        result.refresh_token = refresh_token
    return result


###
# module-private helpers


async def _token_request(
    token_endpoint_url: str, request_body: dict[str, str]
) -> FreshTokenResult:
    _status, _content_type, _payload = await _post_token_request(
        token_endpoint_url, request_body
    )
    if _content_type == "application/x-www-form-urlencoded":
        response_data = dict(urllib.parse.parse_qsl(_payload))
        if expires := response_data.get("expires_in"):
            response_data["expires_in"] = int(expires)

        return FreshTokenResult.from_token_response_json(response_data)
    if not HTTPStatus(_status).is_success:
        raise RuntimeError(
            f"token request to {token_endpoint_url} failed: {_status} {str(_payload)[:200]}"
        )
        # TODO: https://www.rfc-editor.org/rfc/rfc6749.html#section-5.2
    return FreshTokenResult.from_token_response_json(_payload)


async def _post_token_request(
    token_endpoint_url: str, request_body: dict[str, str]
) -> tuple[int, str, str | dict]:
    """returns (status, content_type, payload), payload being text unless json"""
    _client = await get_singleton_client_session()
    async with _client.post(token_endpoint_url, data=request_body) as _response:
        if not urllib_fallback.is_bot_challenge(
            _response.status, _response.content_type
        ):
            return (
                _response.status,
                _response.content_type,
                (
                    await _response.json()
                    if _response.content_type == "application/json"
                    else await _response.text()
                ),
            )
    _buffered = await urllib_fallback.send(
        "POST", token_endpoint_url, data=request_body
    )
    return (
        _buffered.status,
        _buffered.content_type,
        (
            _buffered.json()
            if _buffered.content_type == "application/json"
            else _buffered.text
        ),
    )


def _parse_scope_param_value(scope_value: str | None) -> list[str] | None:
    return None if (scope_value is None) else scope_value.split(_SCOPE_DELIMITER)
