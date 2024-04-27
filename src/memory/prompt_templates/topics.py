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

def create_prompt(problem_description: str) -> str:
    prompt = f"""
    Problem: {problem_description}

    To solve this problem, let's break it down into smaller, manageable steps:

    1. Understand the Problem: Clearly define the problem. What are we trying to solve? What are the inputs and outputs?

    2. Plan the Solution: Outline a step-by-step plan to solve the problem. What functions or methods will we need? What data structures will we use?

    3. Implement the Solution: Write the code for each step of the plan. Test each part individually to ensure it works as expected.

    4. Test the Solution: Once the entire solution is implemented, test it thoroughly to ensure it solves the problem. Consider edge cases and potential pitfalls.

    5. Review and Refine: If the solution doesn't work as expected, review each step to identify where things went wrong. Refine the solution as necessary and repeat the testing process.

    Now, let's start with step 1: Understanding the Problem.
    """
    return prompt

problem_description = "Write a function to find the longest common prefix string amongst an array of strings."
print(create_prompt(problem_description))