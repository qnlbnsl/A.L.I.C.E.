from trieve_client.api.chunk import search_chunk
from trieve_client.api.message import create_message_completion_handler

from trieve_client.models.search_chunk_data import SearchChunkData
from trieve_client.models.search_chunk_query_response_body import (
    SearchChunkQueryResponseBody,
)
from trieve_client.models.create_message_data import CreateMessageData
from trieve_client.models.error_response_body import ErrorResponseBody


from .trieve_manager import TrieveManager
from ..prompt_templates.topics import generate_topic_selection_prompt

from pydantic import StrictStr


class SearchManager(TrieveManager):
    def __init__(self, tm: TrieveManager) -> None:
        self.tm = tm
        self.api_client = tm.api_client
        self.openai_client = tm.openai_client

    def hybrid_search(self, query: str) -> None:
        data = SearchChunkData(query=query, search_type="hybrid")
        resp = search_chunk.sync(
            client=self.api_client, body=data, tr_dataset=self.dataset_id
        )
        if (
            resp is None
            or type(resp) is ErrorResponseBody
            or type(resp) is not SearchChunkQueryResponseBody
        ):
            raise Exception("Error while searching chunks")
        resp.score_chunks.sort(key=lambda x: x.score, reverse=True)

    def _message_completion(self, message: str, topic_id: str) -> StrictStr:
        data = CreateMessageData(
            new_message_content=message, topic_id=topic_id, stream_response=False
        )
        resp = create_message_completion_handler.sync(
            body=data, client=self.api_client, tr_dataset=self.dataset_id
        )
        if (
            resp is None
            or type(resp) is ErrorResponseBody
            or type(resp) is not StrictStr
        ):
            raise Exception("Error while creating message")

        return resp

    def _get_appropriate_topic(self, query: str) -> str:
        prompt = generate_topic_selection_prompt(query, self.tm.topics)
        response = self.openai_client.completions.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.0,
            max_tokens=100,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["\n"],
        )
        response.choices[0].text
        return self.tm.topics[0].id

    def message_completion(self, query: str) -> str:
        topic_id = self._get_appropriate_topic(query)
        return self._message_completion(query, topic_id)
