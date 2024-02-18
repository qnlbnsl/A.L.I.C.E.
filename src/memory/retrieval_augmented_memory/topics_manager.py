from .trieve_manager import TrieveManager
from trieve_client.api.topic import get_all_topics_for_user, create_topic, update_topic
from trieve_client.models.create_topic_data import CreateTopicData
from trieve_client.models.update_topic_data import UpdateTopicData
from trieve_client.models.topic import Topic
from trieve_client.models.error_response_body import ErrorResponseBody


class TopicsManager(TrieveManager):
    def __init__(self, tm: TrieveManager) -> None:
        self.tm = tm
        self.api_client = tm.api_client

    def get_all_topics(self) -> None:
        resp = get_all_topics_for_user.sync(
            client=self.api_client,
            user_id=str(self.user_id),
            tr_dataset=self.dataset_id,
        )
        if resp is None or type(resp) is ErrorResponseBody or type(resp) is not list:
            raise Exception("Error while getting topics")
        self.tm.topics = resp

    def create_topic(self, topic_name: str, message: str) -> None:
        data = CreateTopicData(name=topic_name, first_user_message=message)
        resp = create_topic.sync(
            client=self.api_client, body=data, tr_dataset=self.dataset_id
        )
        if resp is None or type(resp) is ErrorResponseBody or type(resp) is not Topic:
            raise Exception("Error while creating topic")
        self.tm.topics.append(resp)

    def update_topic(self, topic_id: str, new_topic_name: str) -> None:
        data = UpdateTopicData(name=new_topic_name, topic_id=topic_id)
        update_topic.sync(client=self.api_client, body=data, tr_dataset=self.dataset_id)
        self.get_all_topics()
