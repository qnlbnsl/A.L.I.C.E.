import weaviate
import weaviate.classes as wvc
import os
import requests
import json

uri = "weaviate.home.kunalbans.al"
grpc_uri = "grpc.weaviate.home.kunalbans.al"
local_uri = "192.168.1.19"

# client = weaviate.connect_to_custom(  # type: ignore
#     http_host=local_uri,
#     http_port=8080,
#     http_secure=False,
#     grpc_host=local_uri,
#     grpc_secure=False,
#     grpc_port=50051,
#     timeout=(180, 180),  # (connect_timeout, read_timeout)
#     headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")},
# )

client = weaviate.connect_to_custom(  # type: ignore
    http_host=uri,
    http_port=443,  # 8080,
    http_secure=True,
    grpc_host=grpc_uri,
    grpc_secure=False,
    grpc_port=80,  # 50051,
    timeout=(180, 180),  # (connect_timeout, read_timeout)
    headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")},
)

questions = client.collections.get("Question")

response = questions.generate.near_text(
    query="biology",
    limit=2,
    grouped_task="Write a tweet with emojis about these facts.",
)

print(response.generated)
