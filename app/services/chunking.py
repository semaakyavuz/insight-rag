import re

import tiktoken

CHUNK_SIZE_TOKENS = 500
CHUNK_OVERLAP_TOKENS = 50

_ENCODING = tiktoken.get_encoding("cl100k_base")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def chunk_text(
    text: str,
    chunk_size_tokens: int = CHUNK_SIZE_TOKENS,
    overlap_tokens: int = CHUNK_OVERLAP_TOKENS,
) -> list[str]:
    sentences = _split_into_sentences(text)
    if not sentences:
        return []

    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = _count_tokens(sentence)

        if current and current_tokens + sentence_tokens > chunk_size_tokens:
            chunks.append(" ".join(current))
            current, current_tokens = _carry_overlap(current, overlap_tokens)

        current.append(sentence)
        current_tokens += sentence_tokens

    if current:
        chunks.append(" ".join(current))

    return chunks


def _split_into_sentences(text: str) -> list[str]:
    sentences = []
    for paragraph in text.split("\n\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        for sentence in _SENTENCE_SPLIT_RE.split(paragraph):
            sentence = sentence.strip()
            if sentence:
                sentences.append(sentence)
    return sentences


def _carry_overlap(
    sentences: list[str], overlap_tokens: int
) -> tuple[list[str], int]:
    overlap: list[str] = []
    overlap_token_count = 0

    for sentence in reversed(sentences):
        sentence_tokens = _count_tokens(sentence)
        if overlap and overlap_token_count + sentence_tokens > overlap_tokens:
            break
        overlap.insert(0, sentence)
        overlap_token_count += sentence_tokens

    return overlap, overlap_token_count


def _count_tokens(text: str) -> int:
    return len(_ENCODING.encode(text))
