import sys
from unittest.mock import MagicMock, AsyncMock
import pytest

# 1. Create global mocks once and inject them into sys.modules
# This prevents import-time crashes and model downloads across all test files.
global_collection = MagicMock()
global_collection.get.return_value = {"ids": [], "documents": []}

mock_chromadb = MagicMock()
mock_chromadb.PersistentClient.return_value.get_or_create_collection.return_value = global_collection
sys.modules['chromadb'] = mock_chromadb

mock_transformer_instance = MagicMock()
mock_sentence_transformers = MagicMock()
mock_sentence_transformers.SentenceTransformer.return_value = mock_transformer_instance
sys.modules['sentence_transformers'] = mock_sentence_transformers

@pytest.fixture(autouse=True)
def reset_global_mocks():
    global_collection.reset_mock()
    # Keep default return value so _atualizar_bm25 does not fail
    global_collection.get.return_value = {"ids": [], "documents": []}
    mock_transformer_instance.reset_mock()
