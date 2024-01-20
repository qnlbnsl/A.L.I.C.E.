from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.chunk_metadata import ChunkMetadata
from ...models.default_error import DefaultError
from ...types import Response


def _get_kwargs(
    chunk_id: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/chunk/{chunk_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[List["ChunkMetadata"], List["DefaultError"]]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ChunkMetadata.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
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
) -> Response[Union[List["ChunkMetadata"], List["DefaultError"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    chunk_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[List["ChunkMetadata"], List["DefaultError"]]]:
    """
    Args:
        chunk_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[List['ChunkMetadata'], List['DefaultError']]]
    """

    kwargs = _get_kwargs(
        chunk_id=chunk_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    chunk_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[List["ChunkMetadata"], List["DefaultError"]]]:
    """
    Args:
        chunk_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[List['ChunkMetadata'], List['DefaultError']]
    """

    return sync_detailed(
        chunk_id=chunk_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    chunk_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[List["ChunkMetadata"], List["DefaultError"]]]:
    """
    Args:
        chunk_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[List['ChunkMetadata'], List['DefaultError']]]
    """

    kwargs = _get_kwargs(
        chunk_id=chunk_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    chunk_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[List["ChunkMetadata"], List["DefaultError"]]]:
    """
    Args:
        chunk_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[List['ChunkMetadata'], List['DefaultError']]
    """

    return (
        await asyncio_detailed(
            chunk_id=chunk_id,
            client=client,
        )
    ).parsed
