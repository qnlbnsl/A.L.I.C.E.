from .trieve_manager import TrieveManager


class UploadManager(TrieveManager):
    def upload_chunk(self, chunk: bytes, chunk_id: int, total_chunks: int) -> None:
        pass
