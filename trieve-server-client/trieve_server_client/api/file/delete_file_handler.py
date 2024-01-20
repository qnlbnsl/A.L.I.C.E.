from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.default_error import DefaultError
from ...types import Response


def _get_kwargs(
    file_id: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "delete",
        "url": f"/api/file/{file_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, List["DefaultError"]]]:
    if response.status_code == HTTPStatus.NO_CONTENT:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = []
        _response_400 = response.json()
        for response_400_item_data in _response_400:
            response_400_item = DefaultError.from_dict(response_400_item_data)

            response_400.append(response_400_item)

        return response_400
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, List["DefaultError"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    file_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Any, List["DefaultError"]]]:
    """
    Args:
        file_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, List['DefaultError']]]
    """

    kwargs = _get_kwargs(
        file_id=file_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    file_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, List["DefaultError"]]]:
    """
    Args:
        file_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, List['DefaultError']]
    """

    return sync_detailed(
        file_id=file_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    file_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Any, List["DefaultError"]]]:
    """
    Args:
        file_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, List['DefaultError']]]
    """

    kwargs = _get_kwargs(
        file_id=file_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    file_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, List["DefaultError"]]]:
    """
    Args:
        file_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, List['DefaultError']]
    """

    return (
        await asyncio_detailed(
            file_id=file_id,
            client=client,
        )
    ).parsed
