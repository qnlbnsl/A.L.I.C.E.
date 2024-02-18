import time
from trieve_client.api.file import upload_file_handler
from trieve_client.models.upload_file_data import UploadFileData
from trieve_client.models.upload_file_result import UploadFileResult
from trieve_client.models.error_response_body import ErrorResponseBody

from base64 import b64encode

from typing import Any

from ..utils import get_file_content, get_mime_type
from .trieve_manager import TrieveManager
from ..logger import logger


class UploadManager(TrieveManager):
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
    ) -> UploadFileResult:

        resp = upload_file_handler.sync(
            client=self.api_client,
            body=UploadFileData(
                base64_file=str(b64encode(file)),
                create_chunks=True,
                description=description,
                file_mime_type=mime_type,
                file_name=file_name,
                link=link,
                metadata=metadata,
                tag_set=tag_set,
                time_stamp=str(time.time()),
            ),
            tr_dataset=self.dataset_id,
        )
        if (
            resp is None
            or type(resp) is ErrorResponseBody
            or type(resp) is not UploadFileResult
        ):
            raise Exception("Error while uploading file")
        # Contains the file_id as id.
        # track: id, file name, topics/tags?
        logger.debug(resp)
        return resp

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
