import re
import time
import csv

from multiprocessing import Queue
from multiprocessing.synchronize import Event

from text_classification.text_classification import classify_sentence
from logger import logger


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

    def handle_classification(
        self,
        classification: str,
        sentence: str,
        reset: bool,
        question_queue: Queue,
        intent_queue: Queue,

    ):
        logger.debug(
            f"Classification: {UNDERLINE}{RED}{classification.capitalize()}{END} for Sentence: {sentence}"
        )
        match classification:
            case "question":
                if not self.question_override:
                    self.question_override = True
                    for s in self.buffer:  # Dump the entire buffer
                        question_queue.put(s)
                    self.clear_buffer()
                    self.question_len = 1
                elif self.question_len < self.max_question_length:
                    question_queue.put(sentence)
                    self.question_len += 1

                if self.question_len >= self.max_question_length:
                    self.question_override = False
                    self.question_len = 0

            case "command":
                intent_queue.put(sentence)

            # other is not needed....
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


# Modify process_segments function to use the updated SentenceBuffer
def process_segments(
    shutdown_event: Event,
    transcribed_text_queue: Queue,
    question_queue: Queue,
    intent_queue: Queue,
    process_segments_ready_event: Event,
    wake_word_event: Event,
    timeout: float = 5.0,
):
    segment_buffer = SegmentBuffer()
    sentence_buffer = SentenceBuffer()
    process_segments_ready_event.set()
    logger.debug("Ready to process segments")
    while shutdown_event.is_set() is False and wake_word_event.is_set() is True:
        try:
            if not transcribed_text_queue.empty():
                segment = transcribed_text_queue.get()
            else:
                time.sleep(0.1)
                continue
            cleaned_segment = re.sub(r"\.{2,}", ".", segment)
            # this should filter the period that keeps coming in as individual segments
            if len(cleaned_segment) <= 1:
                continue
            segment_buffer.add_segment(cleaned_segment)
            logger.debug(f"segment buffer: {segment_buffer.buffer}")
            logger.debug(f"segment: {cleaned_segment}")
            logger.info(f"Added segment: {segment}")
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
                classification = classify_sentence(sentence)
                # run and forget

                sentence_buffer.handle_classification(
                    classification,
                    sentence,
                    reset=False,
                    question_queue=question_queue,
                    intent_queue=intent_queue,
                )

        except TimeoutError:
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
                # logger.debug("classifying sentence: 2")
                classification = classify_sentence(sentence)

                sentence_buffer.handle_classification(
                    classification,
                    sentence,
                    reset=True,
                    question_queue=question_queue,
                    intent_queue=intent_queue,
                )

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            segment_buffer.clear()
            sentence_buffer.reset()
