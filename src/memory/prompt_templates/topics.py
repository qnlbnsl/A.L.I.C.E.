from typing import List
from trieve_client.models.topic import Topic


def generate_topic_selection_prompt(query: str, topics: List[Topic]) -> str:
    """
    Generates a prompt for selecting the most appropriate topic for a given query,
    given a list of Topic objects.

    Parameters:
    - query (str): The query for which a topic needs to be selected.
    - topics (List[Topic]): A list of Topic objects.

    Returns:
    - str: A prompt formatted for input to OpenAI's API.
    """
    topics_formatted = "\n".join(
        [f"- {topic.name} (ID: {topic.id})" for topic in topics]
    )
    prompt = (
        f"Given the following query, select the most appropriate topic from the list below, "
        f"or indicate if none match. Return the selected topic as a JSON object with the topic ID.\n\n"
        f"Query: {query}\n\n"
        f"Topics:\n{topics_formatted}\n\n"
        f"Response (as JSON):"
    )
    return prompt
