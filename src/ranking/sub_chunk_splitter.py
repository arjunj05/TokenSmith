"""
sub_chunk_splitter.py

Post-retrieval fine-grained sub-chunk splitting and U-shape context ordering.

Instead of passing coarse retrieved chunks directly to the LLM, each chunk is
split into smaller sub-spans that are individually re-scored by the cross-encoder.
The budget-aware selector then picks the most relevant sub-spans, discarding
padding content that is not directly relevant to the query.

U-shape ordering mitigates the "lost in the middle" effect (Liu et al., 2023):
the highest-relevance sub-chunks are placed at the start and end of the context
window where the LLM attends most strongly, with less relevant content in the
middle.
"""

from __future__ import annotations

from typing import List, Tuple, Union

_CONTENT_MARKER = "Content: "


def split_into_sub_chunks(chunk_text: str, fine_chunk_size: int = 400) -> List[str]:
    """
    Split a single coarse chunk into fine-grained sub-chunks.

    If the chunk carries a "Description: ... Content: ..." prefix (added during
    indexing), the prefix is preserved on every sub-chunk so the cross-encoder
    retains section context when scoring each span.

    Parameters
    ----------
    chunk_text : str
        A single chunk as stored in the retrieval index.
    fine_chunk_size : int
        Target character length for each sub-chunk body (excluding the prefix).

    Returns
    -------
    List[str]
        One or more sub-chunks.  Returns the original chunk unchanged when it is
        already shorter than fine_chunk_size.
    """
    if len(chunk_text) <= fine_chunk_size:
        return [chunk_text]

    # Separate section-description prefix from content body
    if _CONTENT_MARKER in chunk_text:
        marker_pos = chunk_text.index(_CONTENT_MARKER) + len(_CONTENT_MARKER)
        prefix = chunk_text[:marker_pos]
        body = chunk_text[marker_pos:]
    else:
        prefix = ""
        body = chunk_text

    if len(body) <= fine_chunk_size:
        return [chunk_text]

    # Non-overlapping fixed-size windows over the body
    sub_chunks = []
    start = 0
    while start < len(body):
        span = body[start : start + fine_chunk_size].strip()
        if span:
            sub_chunks.append(prefix + span)
        start += fine_chunk_size

    return sub_chunks if sub_chunks else [chunk_text]


def order_u_shape(
    chunks: List[Union[str, Tuple[str, float]]],
) -> List[Union[str, Tuple[str, float]]]:
    """
    Reorder chunks so the highest-relevance items sit at the edges of the
    context window, with the least relevant content in the middle.

    Requires (text, score) tuples from the reranker.  Plain strings are
    returned unchanged.

    Placement for n items sorted by descending relevance score:
        position 0    <- rank 1  (most relevant, start of context)
        position n-1  <- rank 2  (second most relevant, end of context)
        position 1    <- rank 3
        position n-2  <- rank 4
        ...

    Parameters
    ----------
    chunks : list
        Selected chunks as (text, score) tuples or plain strings.

    Returns
    -------
    list
        Same type as input, reordered for optimal LLM attention distribution.
    """
    if not chunks or not isinstance(chunks[0], tuple) or len(chunks) <= 2:
        return chunks

    sorted_chunks = sorted(chunks, key=lambda x: x[1], reverse=True)
    result = [None] * len(sorted_chunks)
    left, right = 0, len(sorted_chunks) - 1

    for i, item in enumerate(sorted_chunks):
        if i % 2 == 0:
            result[left] = item
            left += 1
        else:
            result[right] = item
            right -= 1

    return result
