"""
Semantic memory (Part 5): facts that don't depend on the user. The ListenBrainz and MusicBrainz
documentation (knowledge/corpus/) and your glossary (knowledge/glossary.md) are split into chunks,
embedded into Chroma, and searched by the search_music_knowledge tool.

    python semantic.py --build      # (re)build the index; run again after editing the glossary

knowledge/experiment.py compares the two chunking strategies and the hybrid-search improvement,
and is where CHOSEN_STRATEGY and USE_HYBRID below come from.

How it differs from episodic memory: it is written once (when the index is built), not every
session; it is shared knowledge, so it is not filtered by user_id; and it holds no personal data,
so --forget leaves it alone. Imports nothing from encore.py (a leaf module).
"""

import argparse
import os
import re
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions
from rank_bm25 import BM25Okapi

ROOT = Path(__file__).parent
CORPUS_DIR = ROOT / "knowledge" / "corpus"
GLOSSARY_PATH = ROOT / "knowledge" / "glossary.md"
CHROMA_PATH = ROOT / "memory" / "semantic"      # rebuildable from the corpus; memory/ stays out of git

EMBEDDING_MODEL = "all-MiniLM-L6-v2"            # Chroma's default
MODEL_TOKEN_LIMIT = 256     # the model reads at most 256 tokens and silently ignores the rest
SPECIAL_TOKENS = 2          # [CLS] and [SEP] are added to every input and count toward the limit

# Strategy A: fixed windows of tokens, overlapping so a sentence cut at one edge is whole in the next.
FIXED_CHUNK_TOKENS = 256
FIXED_OVERLAP_TOKENS = 32
# Strategy B: one chunk per heading section (one API endpoint, one glossary term), split only if too long.
STRATEGIES = ("fixed", "sections")

# The configuration the tool uses, chosen by knowledge/experiment.py (see knowledge/results.md).
CHOSEN_STRATEGY = "sections"
USE_HYBRID = True

TOP_K = 3                   # passages returned to the model
CANDIDATES = 20             # how many each search method proposes before they are combined
RRF_K = 60                  # reciprocal rank fusion constant (the usual value from the RRF paper)

# Tests replace these with small fakes, so they don't download the real model.
EMBEDDING_FUNCTION = None   # None = Chroma's default (all-MiniLM-L6-v2)
TOKENIZER = None            # None = the model's own tokenizer, loaded on first use

_client = None
_keyword_index = {}         # strategy -> (BM25 index, its chunks); rebuilt when the collection is rebuilt


class KnowledgeBaseMissing(Exception):
    """The index hasn't been built yet."""


# ---------------------------------------------------------------- the documents

def load_documents() -> list[dict]:
    """Every document in the knowledge base: the converted docs plus the glossary."""
    documents = []
    for path in sorted(CORPUS_DIR.glob("*.md")):
        documents.append(_document(path.name, path.read_text(encoding="utf-8")))
    if GLOSSARY_PATH.exists():
        glossary = _document("glossary.md", GLOSSARY_PATH.read_text(encoding="utf-8"))
        glossary["url"] = "knowledge/glossary.md"
        if glossary["text"].count("\n## "):            # skip the empty template
            documents.append(glossary)
    return documents


def _document(name: str, raw: str) -> dict:
    match = re.search(r"<!--\s*source:\s*(\S+)\s*-->", raw)
    if match:
        url = match.group(1)
    else:
        url = ""
    # HTML comments hold notes (the source line, the glossary instructions), not content.
    text = re.sub(r"<!--.*?-->", "", raw, flags=re.S).strip()
    title_match = re.search(r"^# (.+)$", text, flags=re.M)
    if title_match:
        title = title_match.group(1).strip()
    else:
        title = name
    return {"name": name, "title": title, "url": url, "text": text}


# ---------------------------------------------------------------- tokens

def _tokenizer():
    """The embedding model's own tokenizer, without truncation, so we can measure real chunk lengths."""
    global TOKENIZER
    if TOKENIZER is None:
        from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import ONNXMiniLM_L6_V2
        from tokenizers import Tokenizer

        model = ONNXMiniLM_L6_V2()
        model(["warm up"])                                # downloads the model files if needed
        path = os.path.join(model.DOWNLOAD_PATH, model.EXTRACTED_FOLDER_NAME, "tokenizer.json")
        tokenizer = Tokenizer.from_file(path)
        tokenizer.no_truncation()
        tokenizer.no_padding()
        TOKENIZER = tokenizer
    return TOKENIZER


def token_count(text: str) -> int:
    """Tokens the model will see, [CLS] and [SEP] included."""
    return len(_tokenizer().encode(text).ids)


def split_by_tokens(text: str, chunk_tokens: int, overlap: int) -> list[tuple[int, str]]:
    """Cut text into windows of at most chunk_tokens tokens. Returns (start character, chunk text) pairs.

    Adapted from memory_examples/ch07_07_chunking_experiment.py: windows start and end on whole
    words, and the original text is cut at the token boundaries so chunks stay readable.
    """
    content = chunk_tokens - SPECIAL_TOKENS              # leave room for [CLS] and [SEP]
    if overlap >= content:
        raise ValueError("overlap must be smaller than the chunk size")

    encoding = _tokenizer().encode(text, add_special_tokens=False)
    offsets = encoding.offsets
    words = encoding.word_ids
    n = len(offsets)

    def mid_word(i):
        # True if token i continues the word of token i-1.
        return 0 < i < n and words[i] == words[i - 1]

    def is_punctuation(i):
        start, end = offsets[i]
        return not any(ch.isalnum() for ch in text[start:end])

    pieces = []
    start = 0
    while start < n:
        end = min(start + content, n)
        while mid_word(end) and end > start + 1:         # back up to a word boundary
            end -= 1
        piece = text[offsets[start][0]:offsets[end - 1][1]].strip()
        # Safety net for one very long "word" (a URL): trim until it fits.
        while end - start > 1 and token_count(piece) > chunk_tokens:
            end -= 1
            piece = text[offsets[start][0]:offsets[end - 1][1]].strip()
        pieces.append((offsets[start][0], piece))
        if end >= n:
            break
        next_start = max(end - overlap, start + 1)       # step forward, keeping the overlap
        while next_start < end and (mid_word(next_start) or is_punctuation(next_start)):
            next_start += 1
        start = next_start
    return pieces


# ---------------------------------------------------------------- the two chunking strategies

HEADING_RE = re.compile(r"^(#{1,4}) (.+)$")


def _heading_before(text: str, position: int) -> str:
    """The last heading at or before this character, for labelling a chunk with its section."""
    heading = ""
    for match in re.finditer(r"^#{1,4} (.+)$", text[:position + 1], flags=re.M):
        heading = match.group(1).strip()
    return heading


def chunk_fixed(document: dict) -> list[dict]:
    """Strategy A: fixed 256-token windows with 32 tokens of overlap, ignoring the document's structure."""
    chunks = []
    for start, piece in split_by_tokens(document["text"], FIXED_CHUNK_TOKENS, FIXED_OVERLAP_TOKENS):
        chunks.append({"text": piece, "section": _heading_before(document["text"], start)})
    return chunks


def _sections(text: str) -> list[tuple[str, str]]:
    """Split Markdown into (heading line, body) pairs, one per heading."""
    sections = []
    heading = ""
    body_lines = []
    for line in text.splitlines():
        if HEADING_RE.match(line):
            sections.append((heading, "\n".join(body_lines).strip()))
            heading = line.strip()
            body_lines = []
        else:
            body_lines.append(line)
    sections.append((heading, "\n".join(body_lines).strip()))
    return [(heading, body) for heading, body in sections if heading or body]


def chunk_sections(document: dict) -> list[dict]:
    """Strategy B: one chunk per heading section, so an API endpoint or glossary term stays together.

    A heading with no text of its own ("## Explore API") is carried into the next chunk as context.
    A section too long for the model is split into token windows, each starting with its heading.
    """
    chunks = []
    carried = ""                                          # headings waiting for a body
    for heading, body in _sections(document["text"]):
        prefix = (carried + heading).strip()
        if not body:
            carried = prefix + "\n"
            continue
        carried = ""
        label = HEADING_RE.sub(r"\2", heading).strip() if heading else document["title"]

        whole = (prefix + "\n" + body).strip()
        if token_count(whole) <= MODEL_TOKEN_LIMIT:
            chunks.append({"text": whole, "section": label})
            continue

        # Too long: split the body, and repeat the heading on every piece so each stays findable.
        budget = MODEL_TOKEN_LIMIT - (token_count(prefix) - SPECIAL_TOKENS) - 1
        if budget < 64:
            prefix = ""                                   # a huge heading block: drop it rather than starve the text
            budget = MODEL_TOKEN_LIMIT
        for _, piece in split_by_tokens(body, budget, FIXED_OVERLAP_TOKENS):
            chunks.append({"text": (prefix + "\n" + piece).strip(), "section": label})
    return chunks


CHUNKERS = {"fixed": chunk_fixed, "sections": chunk_sections}


def make_chunks(strategy: str, documents=None) -> list[dict]:
    """All chunks for one strategy, each with its source, and every one checked against the token limit."""
    if documents is None:
        documents = load_documents()
    chunks = []
    for document in documents:
        for chunk in CHUNKERS[strategy](document):
            chunk["source"] = document["name"]
            chunk["title"] = document["title"]
            chunk["url"] = document["url"]
            chunks.append(chunk)

    # A chunk over the limit would be silently truncated when embedded: refuse to build.
    for chunk in chunks:
        tokens = token_count(chunk["text"])
        if tokens > MODEL_TOKEN_LIMIT:
            raise ValueError(f"A {strategy} chunk from {chunk['source']} has {tokens} tokens "
                             f"(limit {MODEL_TOKEN_LIMIT}): {chunk['text'][:80]!r}")
    return chunks


# ---------------------------------------------------------------- the index

def _embedding_function():
    if EMBEDDING_FUNCTION is None:
        return embedding_functions.DefaultEmbeddingFunction()
    else:
        return EMBEDDING_FUNCTION


def _get_client():
    global _client
    if _client is None:
        CHROMA_PATH.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return _client


def close() -> None:
    """Forget the open client (tests point CHROMA_PATH somewhere else between tests)."""
    global _client
    _client = None
    _keyword_index.clear()


def _collection_name(strategy: str) -> str:
    return f"knowledge_{strategy}"


def build(strategy: str = CHOSEN_STRATEGY, documents=None) -> int:
    """Chunk, embed, and store the whole knowledge base for one strategy. Returns the chunk count."""
    chunks = make_chunks(strategy, documents)
    client = _get_client()
    try:
        client.delete_collection(_collection_name(strategy))   # a rebuild starts from scratch
    except (chromadb.errors.NotFoundError, ValueError):
        pass
    collection = client.create_collection(
        _collection_name(strategy),
        metadata={"hnsw:space": "cosine", "embedding_model": EMBEDDING_MODEL, "strategy": strategy},
        embedding_function=_embedding_function(),
    )
    for first in range(0, len(chunks), 500):                  # Chroma accepts limited batch sizes
        batch = chunks[first:first + 500]
        collection.add(
            ids=[f"{strategy}-{first + i}" for i in range(len(batch))],
            documents=[chunk["text"] for chunk in batch],
            metadatas=[{"source": chunk["source"], "title": chunk["title"], "url": chunk["url"],
                        "section": chunk["section"], "embedding_model": EMBEDDING_MODEL} for chunk in batch],
        )
    _keyword_index.pop(strategy, None)
    return len(chunks)


def _collection(strategy: str):
    try:
        return _get_client().get_collection(_collection_name(strategy), embedding_function=_embedding_function())
    except (chromadb.errors.NotFoundError, ValueError):
        raise KnowledgeBaseMissing("The music knowledge base hasn't been built yet. "
                                   "Run `python semantic.py --build` once.") from None


# ---------------------------------------------------------------- searching

def keyword_tokens(text: str) -> list[str]:
    """Words for BM25, plus identifier-like strings kept whole.

    An endpoint path such as /1/explore/lb-radio or a header like X-RateLimit-Reset-In becomes one
    rare token ("1/explore/lb-radio"), which keyword search can match exactly even when the
    embedding model can't tell it apart from similar-looking text.
    """
    text = text.lower()
    words = re.findall(r"[a-z0-9]+", text)
    identifiers = re.findall(r"[a-z0-9]+(?:[/_\-.][a-z0-9]+)+", text)
    return words + identifiers


def _result(chunk_id: str, text: str, metadata: dict) -> dict:
    return {"id": chunk_id, "text": text, "source": metadata["source"], "title": metadata["title"],
            "url": metadata["url"], "section": metadata["section"]}


def vector_search(query: str, strategy: str, n: int) -> list[dict]:
    collection = _collection(strategy)
    found = collection.query(query_texts=[query], n_results=n)
    results = []
    for chunk_id, text, metadata, distance in zip(found["ids"][0], found["documents"][0],
                                                  found["metadatas"][0], found["distances"][0]):
        result = _result(chunk_id, text, metadata)
        result["similarity"] = round(1 - distance, 3)
        results.append(result)
    return results


def keyword_search(query: str, strategy: str, n: int) -> list[dict]:
    if strategy not in _keyword_index:
        # Built once per process from the stored chunks, so both searches see the exact same chunks.
        stored = _collection(strategy).get(include=["documents", "metadatas"])
        chunks = []
        for chunk_id, text, metadata in zip(stored["ids"], stored["documents"], stored["metadatas"]):
            chunks.append(_result(chunk_id, text, metadata))
        _keyword_index[strategy] = (BM25Okapi([keyword_tokens(chunk["text"]) for chunk in chunks]), chunks)

    index, chunks = _keyword_index[strategy]
    scores = index.get_scores(keyword_tokens(query))
    ranked = sorted(range(len(chunks)), key=lambda i: scores[i], reverse=True)
    results = []
    for i in ranked[:n]:
        if scores[i] > 0:                                   # no shared words at all: not a match
            results.append(chunks[i])
    return results


def fuse(ranked_lists: list[list[dict]], k: int) -> list[dict]:
    """Reciprocal rank fusion: each list gives a chunk 1 / (RRF_K + rank). Highest total wins.

    It combines rankings instead of raw scores, so BM25 scores (unbounded) and cosine similarities
    (0 to 1) never have to be put on the same scale.
    """
    scores = {}
    chunks = {}
    for ranked in ranked_lists:
        for rank, chunk in enumerate(ranked, start=1):
            scores[chunk["id"]] = scores.get(chunk["id"], 0.0) + 1.0 / (RRF_K + rank)
            chunks[chunk["id"]] = chunk
    best = sorted(scores, key=lambda chunk_id: scores[chunk_id], reverse=True)[:k]
    results = []
    for chunk_id in best:
        chunk = dict(chunks[chunk_id])
        chunk["score"] = round(scores[chunk_id], 4)
        results.append(chunk)
    return results


def search(query: str, strategy: str = CHOSEN_STRATEGY, k: int = TOP_K, hybrid: bool = USE_HYBRID) -> list[dict]:
    """The top k chunks for a query: vector search alone, or fused with keyword search (hybrid)."""
    vector_results = vector_search(query, strategy, CANDIDATES)
    if not hybrid:
        return vector_results[:k]
    return fuse([vector_results, keyword_search(query, strategy, CANDIDATES)], k)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Encore's semantic memory index.")
    parser.add_argument("--build", action="store_true", help="chunk, embed, and store the knowledge base")
    parser.add_argument("--strategy", choices=STRATEGIES, default=CHOSEN_STRATEGY)
    args = parser.parse_args()
    if args.build:
        documents = load_documents()
        count = build(args.strategy, documents)
        print(f"Built '{args.strategy}' index: {len(documents)} documents, {count} chunks, model {EMBEDDING_MODEL}.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
