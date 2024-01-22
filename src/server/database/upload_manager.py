from .trieve_manager import ArguflowManager


class UploadManager(ArguflowManager):
    def upload_chunk(self, chunk: bytes, chunk_id: int, total_chunks: int) -> None:
        pass
