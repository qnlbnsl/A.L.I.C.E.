from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_topic_data import CreateTopicData
from ...models.default_error import DefaultError
from ...models.topic import Topic
from ...types import Response


def _get_kwargs(
    *,
    body: CreateTopicData,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/api/topic",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[List["DefaultError"], List["Topic"]]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Topic.from_dict(response_200_item_data)

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
) -> Response[Union[List["DefaultError"], List["Topic"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CreateTopicData,
) -> Response[Union[List["DefaultError"], List["Topic"]]]:
    """create_topic

     create_topic

    Create a new chat topic. Topics are attached to a user and act as a coordinator for memory of gen-AI
    chat sessions.

    Args:
        body (CreateTopicData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[List['DefaultError'], List['Topic']]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CreateTopicData,
) -> Optional[Union[List["DefaultError"], List["Topic"]]]:
    """create_topic

     create_topic

    Create a new chat topic. Topics are attached to a user and act as a coordinator for memory of gen-AI
    chat sessions.

    Args:
        body (CreateTopicData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[List['DefaultError'], List['Topic']]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CreateTopicData,
) -> Response[Union[List["DefaultError"], List["Topic"]]]:
    """create_topic

     create_topic

    Create a new chat topic. Topics are attached to a user and act as a coordinator for memory of gen-AI
    chat sessions.

    Args:
        body (CreateTopicData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[List['DefaultError'], List['Topic']]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CreateTopicData,
) -> Optional[Union[List["DefaultError"], List["Topic"]]]:
    """create_topic

     create_topic

    Create a new chat topic. Topics are attached to a user and act as a coordinator for memory of gen-AI
    chat sessions.

    Args:
        body (CreateTopicData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[List['DefaultError'], List['Topic']]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
