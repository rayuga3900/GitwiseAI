import pytest
from gitwise.core import DataLoader, Chunker, Embedder
from unittest.mock import MagicMock

@pytest.fixture
def loader():
    return DataLoader(
        repo_url="https://github.com/rayuga3900/Power-Consumption-Predictor",
        clone_root="test_data",
        branch="main"
    )

@pytest.fixture
def chunker():
    return Chunker(chunk_size=500, overlap=50)

@pytest.fixture
def fake_embedder():
    fake = MagicMock(spec=Embedder)
    fake.embed_chunks.side_effect = lambda texts: [[0.1]*384 for _ in texts]
    return fake