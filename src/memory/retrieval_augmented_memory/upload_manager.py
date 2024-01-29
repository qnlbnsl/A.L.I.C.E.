import time
from trieve_python_client.api.file_api import FileApi
from trieve_python_client.models.upload_file_data import UploadFileData
from base64 import b64encode

from typing import Any

from ..utils import get_file_content, get_mime_type
from .trieve_manager import TrieveManager
from ..logger import logger


class UploadManager:
    def __init__(self, tm: TrieveManager) -> None:
        self.api_client = tm.api_client

    def _upload_file(
        self,
        file: bytes,
        file_name: str,
        mime_type: str,
        description: str | None,
        link: str | None,
        metadata: Any | None,
        tag_set: list[str] | None,
    ) -> None:
        file_api_client = FileApi(self.api_client)
        if tag_set is not None:
            tags = ",".join(tag_set)
        else:
            tags = None
        resp = file_api_client.upload_file_handler(
            upload_file_data=UploadFileData(
                base64_file=str(b64encode(file)),
                create_chunks=True,
                description=description,
                file_mime_type=mime_type,
                file_name=file_name,
                link=link,
                metadata=metadata,
                tag_set=tags,
                time_stamp=str(time.time()),
            )
        )
        # Contains the file_id as id.
        # track: id, file name, topics/tags?
        logger.debug(resp)

    def upload(self, path_or_url: str) -> None:
        file_buffer = get_file_content(path_or_url)
        mime_type = get_mime_type(file_buffer)
        file_name = path_or_url.split("/")[-1]

        try:
            self._upload_file(
                file=file_buffer,
                file_name=file_name,
                mime_type=mime_type,
                description=None,
                link=path_or_url,
                metadata=None,
                tag_set=None,
            )
        except Exception as e:
            logger.error(e)
            raise e
