from unittest.mock import MagicMock, patch

from llama_index.core.graph_stores.types import GraphStore
from llama_index.graph_stores.arangodb import ArangoDBGraphStore

@patch("llama_index.graph_stores.arangodb.ArangoDBGraphStore")
def test_kuzu_graph_store(MockArangoDBGraphStore: MagicMock):
    instance: ArangoDBGraphStore = MockArangoDBGraphStore.return_value()
    assert isinstance(instance, GraphStore)