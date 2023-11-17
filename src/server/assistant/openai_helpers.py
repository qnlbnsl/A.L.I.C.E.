from typing import List
from assistant.assistants import (
    threads,
    run_thread,
    message_thread,
    chat_completion,
)
from openai.types.beta import Thread
from openai.types.chat import ChatCompletionMessageParam


async def parse_command():
    # Parse the intent
    pass


async def parse_question(questions: List[ChatCompletionMessageParam]):
    rs = chat_completion.create(
        model="gpt-4-1106-preview", stream=True, temperature=0.0, messages=questions
    )
    # Parse the question
    collected_ev = []
    total_reply = ""
    for ev in rs:
        collected_ev.append(ev)
        for choice in ev.choices:
            if choice.finish_reason == "stop":
                print(total_reply)
                return total_reply
            else:
                if choice.delta.content is not None:
                    total_reply += choice.delta.content
                    print(choice.delta.content)
    pass


async def parse_concept():
    # Parse the concept
    # perform heavier processing and then send the result to the concept assistant
    pass
