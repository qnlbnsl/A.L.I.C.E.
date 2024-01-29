from typing import List
from .trieve_manager import TrieveManager
from trieve_python_client.api.topic_api import TopicApi
from trieve_python_client.models.create_topic_data import CreateTopicData
from trieve_python_client.models.update_topic_data import UpdateTopicData
from trieve_python_client.models.topic import Topic


class SearchManager:
    def __init__(self, tm: TrieveManager) -> None:
        self.api_client = tm.api_client
        self.topics: List[Topic] = []

    def get_all_topics(self) -> None:
        topic_client = TopicApi(self.api_client)
        resp = topic_client.get_all_topics()
        self.topics = resp

    def create_topic(self, topic_name: str, message: str) -> None:
        topic_client = TopicApi(self.api_client)
        data = CreateTopicData(name=topic_name, first_user_message=message)
        resp = topic_client.create_topic(data)
        self.topics.append(resp)

    def update_topic(self, topic_id: str, new_topic_name: str) -> None:
        topic_client = TopicApi(self.api_client)
        data = UpdateTopicData(name=new_topic_name, topic_id=topic_id)
        topic_client.update_topic(data)
        self.get_all_topics()
