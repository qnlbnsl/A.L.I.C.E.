from arguflow_server_client import AuthenticatedClient
from arguflow_server_client.api.topic import create_topic, get_all_topics
from arguflow_server_client.models import CreateTopicData

client = AuthenticatedClient(
    "http://docker-standalone.local:8090",
    token="supersecretkey",
)

data = CreateTopicData(
    name="test",
    normal_chat=False,
)

# create_topic.sync_detailed(client=client, body=data)
resp = get_all_topics.sync_detailed(client=client)

print(resp)

# Available modules:
# auth, chunk, chunk_collection, dataset, file, health, message, notifications, organization, topic, user
