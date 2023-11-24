from typing import Dict, List, Tuple
from llama_cpp import Llama
from logger import logger

# import csv

# data = csv.reader(
#     open(
#         "/home/qnlbnsl/ai_voice_assistant/src/server/assistant/training_data/train.csv"
#     ),
#     delimiter=",",
# )
llama_7b = "/home/qnlbnsl/ai_voice_assistant/models/7B/llama-2-7b.Q4_K_M.gguf"
llama_13b = "/home/qnlbnsl/ai_voice_assistant/models/13B/llama-2-13b.Q4_K_M.gguf"
# chat_format = "llama-2"
chat_format = "chatml"
llm = Llama(
    model_path=llama_13b,
    chat_format=chat_format,
    n_threads=8,
    n_gpu_layers=12,  # 13b model has 43 layers
    n_ctx=2048,
)


def extract_classification(response: str) -> str:
    try:
        classification = response.split("\nClassification: ")[1].strip()
        return classification.replace('"', "").replace("'", "").strip()
    except IndexError:
        return "Error"  # Return "Error" if parsing fails


def chat_completion(message):
    # prompt = f"Classify the following sentence into one of these categories - 'question', 'command', and 'other'. A command is any sentence that wants to perform an action on an object. A question is any sentence that requests specific information. If a text is neither a question or a command then classify text as 'other'. Respond with only the category name.: \n\nSentence: \"{message}\" \nClassification:"
    prompt = (
        "Classify the following sentence into one of these categories - 'question', 'command', or 'other'. "
        "Respond only with one of these words: 'question', 'command', or 'other'. "
        "A 'command' is a directive to perform an action."
        "A 'question' seeks specific information."
        "If a sentence is neither a direct action nor a specific inquiry, classify it as 'other'."
        "Command Example: "
        "'Turn off the lights.' 'Lock all the doors.' 'Start the coffee maker.' -> 'command' "
        "Question Example: "
        "'What is the time now?' 'What is the weather like today?' 'What is the capital of France?' -> 'question' "
        "Other Example: "
        "'The omniscient narrator in literature sees and knows all, like a god of their created world.' 'The Sapir-Whorf hypothesis argues that language determines thought.' 'Cognitive dissonance is the mental discomfort experienced by holding contradictory beliefs.' 'What is going on?' 'How are you?' -> 'other' \n\n"
        'Sentence: "{}" \nClassification:'.format(message)
    )
    return llm(prompt=prompt, max_tokens=15, temperature=0.5, stop=["\n"], echo=True)


test_data = {
    "question": [
        "Can you recommend a good mystery novel?",
        "Why do leaves change color in the fall?",
        "How do you bake a chocolate cake?",
        "What's the capital of France?",
        "Who won the Nobel Prize in Physics last year?",
        "How many planets are in our solar system?",
        "What is the largest mammal on Earth?",
        "How is the weather today?",
        "How is the weather outside?",
        "What is the stock price for tesla?",
        "What are the current fashion week dates for Milan?",
        "What are the fashion week dates for Milan this year?",
        "What's the unemployment rate in the United States?",
        "What are the daily recommended nutritional guidelines?",
        "Who is the most followed person on Instagram at the moment?",
        "When is the next SpaceX launch?",
        "What is the current price of Bitcoin?",
        "Are there any severe weather warnings in effect for Florida?",
        "How much traffic is on the I-95 at this moment?",
        "What is quantum computing?",
        "How did IBM achieve quantum supremacy?",
        "What is the difference between a quantum computer and a classical computer?",
        "Can i mix bleach and ammonia?",
    ],
    "command": [
        "Lock all the doors",
        "Close the garage door",
        "Turn on the porch light",
        "Start the coffee maker",
        "Activate the alarm system",
        "Set the bedroom lights to warm white",
        "Turn on the ceiling fan in the living room",
        "Increase the fridge temperature by two degrees",
        "Show me the backyard camera feed",
        "Start recording on the security camera",
        "Play my workout playlist in the home gym",
        "Turn off all lights upstairs",
        "Set a timer for 20 minutes for the oven",
        "Pause the dishwasher cycle",
        "Resume the robot vacuum cleaning",
        "Turn on the holiday lighting scene",
        "Activate the garden sprinklers",
        "Set the hot tub temperature to 100 degrees",
        "Turn on the dining room lights at 7 PM",
        "Adjust the living room lights for reading",
        "Can you please turn on the TV",
        "Can you please turn on the living room lights",
        "Can you please make me some coffee",
        "Can you please water the plants",
    ],
    "other": [
        "The omniscient narrator in literature sees and knows all, like a god of their created world",
        "The Sapir-Whorf hypothesis argues that language determines thought",
        "Cognitive dissonance is the mental discomfort experienced by holding contradictory beliefs",
        "The Mandela effect is when a large group of people remembers something differently than how it occurred",
        "The Overton window frames the range of policies politically acceptable to the mainstream at a given time",
        "The paradox of thrift posits that individual savings can lead to a collective economic downturn",
        "The law of diminishing returns states that successive increases in inputs yield progressively smaller increases in outputs",
        "The Great Filter theory suggests there is a barrier to the development of advanced civilizations",
        "The Fermi paradox ponders the apparent absence of extraterrestrial life despite its high probability",
        "The concept of wabi-sabi embraces the beauty of imperfection and transience",
        "The Peter principle states that people in a hierarchy tend to rise to their level of incompetence",
        "The Baader-Meinhof phenomenon is the illusion that something newly learned suddenly appears everywhere",
        "The principle of charity suggests interpreting others' statements in the most rational way possible",
        "The narrative fallacy is the tendency to fit events into a story after they have happened",
        "The concept of an omniverse encompasses every universe, multiverse, and possibility.",
        "The Ship of Theseus paradox explores the nature of identity and change",
        "The Rorschach test uses inkblots to delve into the subconscious mind",
        "Autonomy in technology raises ethical questions about the role of human oversight",
        "The paradox of tolerance highlights the need to limit tolerance to preserve an open society",
        "Shadow work refers to unpaid labor, such as self-service checkout, that benefits companies.",
        "The concept of a technological singularity reflects the point where AI surpasses human intelligence",
        "Collective intelligence emerges when groups act in ways that seem intelligent",
        "The Hawthorne effect is the alteration of behavior by study subjects due to their awareness of being observed",
        "Of course.",
        "You have 20 seconds left on your alarm.",
        "You have 5 new notifications",
        "Your package has been delivered.",
        "What's going on?",  # Too vague to be a question.
        "It's very popular.",
    ],
}


def collect_responses(test_data: Dict[str, List[str]]) -> List[Tuple[str, str]]:
    responses = []
    for category, sentences in test_data.items():
        for sentence in sentences:
            output = chat_completion(sentence)
            response = output["choices"][0]["text"]  # type: ignore
            responses.append((sentence, response))
    return responses


def evaluate_responses(
    responses: List[Tuple[str, str]], test_data: Dict[str, List[str]]
):
    total_tests = 0
    correct = 0

    for sentence, response in responses:
        classification = extract_classification(response)
        expected_category = next(
            (cat for cat, sentences in test_data.items() if sentence in sentences),
            "Unknown",
        )

        total_tests += 1
        if classification.lower() == expected_category:
            correct += 1
        else:
            if expected_category == "other" and "other" in classification.lower():
                correct += 1
            else:
                logger.error(
                    f"Expected: {expected_category}, Actual: {classification}, Sentence: {sentence}"
                )

    logger.info(
        f"Total tests: {total_tests}, Correct: {correct}, Accuracy: {correct / total_tests:.2%}"
    )


# Collect responses
responses = collect_responses(test_data)

# Evaluate responses
evaluate_responses(responses, test_data)
