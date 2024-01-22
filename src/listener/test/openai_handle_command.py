import csv
import os
import time
from typing import cast
from logger import logger
from openai import OpenAI
from openai.types.beta.threads import MessageContentText

api_key = os.environ.get("OPENAI_API_KEY") if os.environ.get("OPENAI_API_KEY") else None
client = OpenAI(api_key=api_key)
assistants = client.beta.assistants
chat_completion = client.chat.completions
threads = client.beta.threads
message_thread = client.beta.threads.messages
run_thread = client.beta.threads.runs

intent_assistant = assistants.retrieve(assistant_id="asst_7kZM2CL3yegIGzhMsxAfKz5k")


def add_message_to_thread(thread_id, message):
    message_thread.create(thread_id=thread_id, content=message, role="user")


# Define the testing function
def test_intent_classification(csv_filepath):
    with open(csv_filepath, "r") as csv_file:
        reader = csv.reader(csv_file, delimiter="|")
        total = 0
        false_positives = 0

        for row in reader:
            label, statement, label_id = row
            expected_output = label_id in [
                "1"
            ]  # Assuming '1' is the label for commands
            output = classify_intent(statement)
            if output != expected_output and expected_output is False:
                false_positives += 1
            total += 1

        detection_rate = false_positives / total
        logger.info(f"Detection Rate for False Positives: {detection_rate}")
        return detection_rate


def classify_intent(intent):
    logger.debug(intent)
    intent_thread = threads.create()
    add_message_to_thread(thread_id=intent_thread.id, message=intent)
    run = run_thread.create(
        thread_id=intent_thread.id, assistant_id=intent_assistant.id
    )
    output = time.time() % 2 == 0
    while run.status != "completed":
        time.sleep(1)
        run = run_thread.retrieve(thread_id=intent_thread.id, run_id=run.id)
        if (
            run.status == "requires_action"
            and run.required_action
            and run.required_action.type == "submit_tool_outputs"
        ):
            tool_outputs = []
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                function_call_id = tool_call.id
                function_name = tool_call.function.name
                arguments = tool_call.function.arguments
                # logger.debug(function_call_id)
                # logger.debug(function_name)
                logger.debug(arguments)
                # TODO: Add the function call to the intent queue
                tool_outputs.append(
                    {"tool_call_id": function_call_id, "output": f"{output}"}
                )
                # output = not output
            # logger.debug(f"Submitting tool outputs: {tool_outputs}")
            run_thread.submit_tool_outputs(
                thread_id=intent_thread.id, run_id=run.id, tool_outputs=tool_outputs
            )

    messages = message_thread.list(thread_id=intent_thread.id)
    logger.debug(messages)
    response = cast(MessageContentText, messages.data[0].content[0]).text.value
    threads.delete(thread_id=intent_thread.id)
    return response


csv_file = "/home/qnlbnsl/ai_voice_assistant/src/server/text_classification/training_data/eval.csv"

labels_dict = {"question": 2, "command": 1, "other": 0}
# if label is 0 or 2 then expected output is None. If label is 1 then expected output is True
if __name__ == "__main__":
    test_intent_classification(csv_file)
    # classify_intent("Turn on all the lights")
