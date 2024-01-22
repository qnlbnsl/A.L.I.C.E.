from typing import List, Self
import time
import re

class SegmentBuffer:
    def __init__(self: Self) -> None:
        self.buffer = ""
        self.last_update_time = time.time()

    def add_segment(self: Self, segment: str) -> None:
        self.buffer += " " + segment.strip()
        self.last_update_time = time.time()

    def clear(self: Self) -> None:
        self.buffer = ""
        self.last_update_time = time.time()

    def detect_sentences(self: Self) -> List[str]:
        punctuation_pattern = r"(\.\.\.|[.!?])"
        matches = re.finditer(punctuation_pattern, self.buffer)
        sentences: List[str] = []

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
