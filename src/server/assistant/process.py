import re
from multiprocessing import Queue

from multiprocessing.synchronize import Event
from typing import List

from assistant.buffers.question_buffer import QuestionBuffer
from assistant.buffers.segment_buffer import SegmentBuffer
from text_classification.text_classification import classify_sentence

from logger import logger


# ANSI escape codes
RED = "\033[91m"
UNDERLINE = "\033[4m"
END = "\033[0m"

# Modify process_segments function to use the updated SentenceBuffer
def process_segments(
    shutdown_event: Event,
    transcribed_text_queue: "Queue[str]",
    question_queue: "Queue[str]",
    intent_queue: "Queue[str]",
    process_segments_ready_event: Event,
    question_event: Event,
    timeout: float = 5.0,
) -> None:
    segment_buffer = SegmentBuffer()
    question_buffer = QuestionBuffer(question_queue=question_queue, timeout=timeout)
    process_segments_ready_event.set()
    logger.debug("Ready to process segments")
    while shutdown_event.is_set() is False:
        try:
            segment = transcribed_text_queue.get() # Wait for segment to be available
            
            # This should filter the period that keeps coming in as individual segments
            cleaned_segment = re.sub(r"\.{2,}", ".", segment) 
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

            sentences: List[str] = segment_buffer.detect_sentences()
            for sentence in sentences:
                # Bypass classification if question is in progress.
                if question_event.is_set():
                    question_buffer.handle_question(sentence=sentence, question_event=question_event)
                    continue
                
                # Sentence should be at least 10 characters long.
                if len(sentence) <= 15:
                    continue
                
                classification = classify_sentence(sentence)

                if classification == "question":
                    # Set question event to prevent other processes from classifying.
                    question_event.set()
                    question_buffer.handle_question(
                        sentence,
                        question_event=question_event,
                    )
                elif classification == "intent":
                    intent_queue.put(sentence)
                else:
                    logger.debug(
                        f"Classification: {classification}, Sentence: {sentence}"
                    )


        except TimeoutError:
            # if question_buffer._check_timeout():
            #     logger.debug("Question timeout occurred, clearing buffer")
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

                question_buffer.handle_question(
                    sentence=sentence,
                    question_event=question_event,
                )

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            segment_buffer.clear()
