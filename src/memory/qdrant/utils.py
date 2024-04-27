from pathlib import Path

from typing import Dict


def get_file_metadata(file_name: str) -> Dict[str, str]:
    """Get file metadata."""
    date_str = Path(file_name).stem.split("_")[1:4]
    return {"date": "-".join(date_str)}
