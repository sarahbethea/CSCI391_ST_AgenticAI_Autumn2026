"""Shared setup for the unit layer: every test gets its own empty memory stores."""

import math

import pytest
from chromadb import Documents, EmbeddingFunction, Embeddings

import episodic
import hot_state


class WordCountEmbedding(EmbeddingFunction):
    """A tiny stand-in for the real embedding model: counts words into 64 buckets.

    Texts that share words get similar vectors, which is all the episodic tests need, and it
    needs no download. Normalized so cosine similarity behaves like the real model's.
    """

    def __init__(self):
        pass

    def __call__(self, input: Documents) -> Embeddings:
        vectors = []
        for text in input:
            vector = [0.0] * 64
            for word in text.lower().split():
                vector[sum(ord(c) for c in word) % 64] += 1.0
            length = math.sqrt(sum(x * x for x in vector)) or 1.0
            vectors.append([x / length for x in vector])
        return vectors

    @staticmethod
    def name() -> str:
        return "word-count-test"

    def get_config(self) -> dict:
        return {}

    @staticmethod
    def build_from_config(config: dict) -> "WordCountEmbedding":
        return WordCountEmbedding()


@pytest.fixture(autouse=True)
def isolated_hot_state(tmp_path, monkeypatch):
    """Point hot state at a temporary file, so no unit test reads or writes the real memory/ folder."""
    hot_state.close()
    monkeypatch.setattr(hot_state, "DB_PATH", tmp_path / "hot_state.db")
    yield
    hot_state.close()


@pytest.fixture(autouse=True)
def isolated_episodic(tmp_path, monkeypatch):
    """A temporary Chroma folder and the fake embedding function, for every unit test."""
    episodic.close()
    monkeypatch.setattr(episodic, "CHROMA_PATH", tmp_path / "chroma")
    monkeypatch.setattr(episodic, "EMBEDDING_FUNCTION", WordCountEmbedding())
    yield
    episodic.close()
