from .search_manager import SearchManager
from .trieve_manager import TrieveManager
from .upload_manager import UploadManager

__all__ = ["TrieveManager", "SearchManager", "UploadManager"]

if __name__ == "__main__":
    tm = TrieveManager("http://192.168.3.205", 8090, "supersecretkey")
    sm = SearchManager(tm)
    um = UploadManager(tm)
