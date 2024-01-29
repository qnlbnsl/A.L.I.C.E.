from .trieve_manager import TrieveManager
from trieve_python_client.api.chunk_api import ChunkApi
from trieve_python_client.models.search_chunk_data import SearchChunkData
from trieve_python_client.api.message_api import MessageApi
from trieve_python_client.models.create_message_data import CreateMessageData


class SearchManager:
    def __init__(self, tm: TrieveManager) -> None:
        self.api_client = tm.api_client
        self.topics = []

    def hybrid_search(self, query: str) -> None:
        search_client = ChunkApi(self.api_client)
        data = SearchChunkData(query=query, search_type="hybrid")
        resp = search_client.search_chunk(search_chunk_data=data)
        resp.score_chunks.sort(key=lambda x: x.score, reverse=True)

    def _message_completion(self, message: str, topic_id: str) -> None:
        message_client = MessageApi(self.api_client)
        data = CreateMessageData(
            new_message_content=message, topic_id=topic_id, stream_response=False
        )
        message_client.create_message_completion_handler(data)

