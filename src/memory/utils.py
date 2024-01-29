import requests
import magic
import os


def get_file_content(source: str) -> bytes:
    # Check if source is a URL
    if source.startswith("http://") or source.startswith("https://"):
        response = requests.get(source)
        response.raise_for_status()  # Ensure the request was successful
        return response.content
    # Else, assume it's a file path
    else:
        if os.path.exists(source):
            with open(source, "rb") as file:
                return file.read()
        else:
            raise FileNotFoundError(f"The file '{source}' was not found.")


def get_mime_type(buffer: bytes) -> str:
    return magic.from_buffer(buffer, mime=True)
