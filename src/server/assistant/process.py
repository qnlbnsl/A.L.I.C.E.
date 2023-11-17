import asyncio
import time
from typing import List
from logger import logger
import re
import spacy
import csv

from assistant.intents.parse_intent import intent_queue
from assistant.concept_store.parse_concept import concept_queue
from assistant.questions.parse_question import question_queue

transcribed_text_queue = asyncio.Queue()


def import_and_organize_data(file_path):
    data = {}
    with open(file_path, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            type_key = row["type"]
            text = row["text"]
            if type_key not in data:
                data[type_key] = []
            data[type_key].append(text)
    return data


# ANSI escape codes
RED = "\033[91m"
UNDERLINE = "\033[4m"
END = "\033[0m"
data = import_and_organize_data("src/server/assistant/training_data/train.csv")
# logger.debug(data)
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
        "Can you please turn on the TV?",
        "Can you please turn on the living room lights?",
        "Can you please make me some coffee?",
        "Can you please water the plants?",
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


nlp_v2 = spacy.blank("en")
nlp_v2.add_pipe(
    "classy_classification",
    config={
        "data": test_data,
        "model": "sentence-transformers/all-mpnet-base-v2",
        "device": "gpu",
    },
)


class SegmentBuffer:
    def __init__(self):
        self.buffer = ""
        self.last_update_time = time.time()

    def add_segment(self, segment: str):
        self.buffer += " " + segment.strip()
        self.last_update_time = time.time()

    def clear(self):
        self.buffer = ""
        self.last_update_time = time.time()

    def detect_sentences(self):
        punctuation_pattern = r"(\.\.\.|[.!?])"
        matches = re.finditer(punctuation_pattern, self.buffer)
        sentences = []

        start_idx = 0
        for match in matches:
            end_idx = match.end()
            sentence = self.buffer[start_idx:end_idx].strip()
            if (
                sentence and len(sentence) > 1
            ):  # Filter out single-character 'sentences'
                sentences.append(sentence)
            start_idx = end_idx

        self.buffer = self.buffer[start_idx:].lstrip()
        return sentences


class SentenceBuffer:
    def __init__(self):
        self.buffer = []
        self.question_override = False
        self.question_len = 0
        self.max_question_length = 10
        self.last_update_time = time.time()

    def add_segment(self, segment: str):
        self.buffer.append(segment.strip())
        self.last_update_time = time.time()
        if len(self.buffer) > self.max_question_length:
            self.buffer.pop(0)

    def reset(self):
        self.buffer = []
        self.question_override = False
        self.question_len = 0

    def clear_buffer(self):
        self.buffer = []

    def clear_question(self):
        self.question_override = False
        self.question_len = 0

    async def handle_classification(
        self, classification: str, sentence: str, reset: bool
    ):
        logger.debug(
            f"Classification: {UNDERLINE}{RED}{classification.capitalize()}{END} for Sentence: {sentence}"
        )
        match classification:
            case "question":
                if not self.question_override:
                    self.question_override = True
                    for s in self.buffer:  # Dump the entire buffer
                        await question_queue.put(s)
                    self.clear_buffer()
                    self.question_len = 1
                elif self.question_len < self.max_question_length:
                    await question_queue.put(sentence)
                    self.question_len += 1

                if self.question_len >= self.max_question_length:
                    self.question_override = False
                    self.question_len = 0

            case "command":
                await intent_queue.put(sentence)

            # not needed....
            # case "other":
            # await concept_queue.put(sentence)
            case _:
                # logger.debug(f"Other/Unknown classification detected for: {sentence}")
                pass
                # if len(sentence) > 10:
                #     await concept_queue.put(sentence)
        if reset:
            self.reset()

    def check_timeout(self, timeout):
        if time.time() - self.last_update_time > timeout and self.question_override:
            self.question_override = False
            self.question_len = 0
            return True
        return False


async def classify_sentence(sentence: str) -> str:
    # logger.debug(f"Classifying sentence: {sentence}")
    doc = nlp_v2(sentence)
    # logger.debug(doc._.cats)
    if doc._.cats:
        # Find the category with the maximum score
        category = max(doc._.cats, key=doc._.cats.get)  # type: ignore
        return category
    else:
        return "Other"  # Return a default value if doc.cats is empty


# Modify process_segments function to use the updated SentenceBuffer
async def process_segments(timeout: float = 5.0):
    segment_buffer = SegmentBuffer()
    sentence_buffer = SentenceBuffer()

    while True:
        try:
            segment = await asyncio.wait_for(transcribed_text_queue.get(), timeout)
            cleaned_segment = re.sub(r"\.{2,}", ".", segment)
            # this should filter the period that keeps coming in as individual segments
            if len(cleaned_segment) <= 1:
                continue
            segment_buffer.add_segment(cleaned_segment)
            # logger.debug(f"segment buffer: {segment_buffer.buffer}")
            # logger.debug(f"segment: {cleaned_segment}")
            # logger.info(f"Added segment: {segment}")
            # if segment is small then skip classification and continue
            if len(cleaned_segment) <= 10:
                logger.info(
                    f"Skipping classification for segment due to small sample size: {cleaned_segment}"
                )
                continue

            sentences = segment_buffer.detect_sentences()
            for sentence in sentences:
                # sentence should be at least 10 characters long
                if len(sentence) <= 15:
                    continue
                logger.debug("classifying sentence: 1")
                classification = await classify_sentence(sentence)
                # run and forget
                asyncio.create_task(
                    sentence_buffer.handle_classification(
                        classification, sentence, reset=False
                    )
                )

        except asyncio.TimeoutError:
            if sentence_buffer.check_timeout(timeout):
                logger.debug("Question timeout occurred, clearing buffer")
            if segment_buffer.buffer.strip():
                sentence = segment_buffer.buffer.strip()
                segment_buffer.clear()
                if len(sentence) <= 15:
                    # skip classification and continue
                    logger.info(
                        f"Skipping classification for sentence due to small sample size: {sentence}"
                    )
                    continue
                logger.debug("classifying sentence: 2")
                classification = await classify_sentence(sentence)
                asyncio.create_task(
                    sentence_buffer.handle_classification(
                        classification, sentence, reset=True
                    )
                )

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            segment_buffer.clear()
            sentence_buffer.reset()


async def initialize_assistant():
    await process_segments()
