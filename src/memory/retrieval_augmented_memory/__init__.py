from .search_manager import SearchManager
from .trieve_manager import TrieveManager
from .upload_manager import UploadManager
from .topics_manager import TopicsManager

__all__ = ["TrieveManager", "SearchManager", "UploadManager", "TopicsManager"]

if __name__ == "__main__":
    import os

    host = "http://192.168.3.205"
    port = 8090

    api_key = "YOUR_API_KEY"
    openai_api_key = "YOUR_OPENAI_API_KEY"

    dataset_id = os.getenv("TRIEVE_DATASET_ID")
    organization_id = os.getenv("TRIEVE_ORGANIZATION_ID")

    tr_mgr = TrieveManager(
        host=host,
        port=port,
        api_key=api_key,
        openai_api_key=openai_api_key,
        org_id=organization_id,
        dataset_id=dataset_id,
    )
    srch_mgr = SearchManager(tr_mgr)
    upl_mgr = UploadManager(tr_mgr)
    tpc_mgr = TopicsManager(tr_mgr)
    tpc_mgr.get_all_topics()
