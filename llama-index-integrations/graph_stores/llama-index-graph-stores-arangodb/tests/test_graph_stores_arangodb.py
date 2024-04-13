
from llama_index.graph_stores.arangodb import ArangoDBGraphStore

from llama_index.core import SimpleDirectoryReader, KnowledgeGraphIndex

from llama_index.llms.openai import OpenAI
from llama_index.core import Settings

# Preperation
import os
os.environ["OPENAI_API_KEY"] = "API_KEY_HERE"

adb_host = "http://localhost:8529"
adb_username = "root"
adb_password ="openSesame"
adb_database = "test"

graph_store = ArangoDBGraphStore(
    arangodb_host = adb_host,
    username = adb_username,
    password = adb_password,
    database = adb_database,
)



storage_context = StorageContext.from_defaults(graph_store=graph_store)
index = KnowledgeGraphIndex.from_documents(
    documents,
    storage_context=storage_context,
    max_triplets_per_chunk=2,
)
#Querying the Knowledge Graph
#First, we can query and send only the triplets to the LLM.

query_engine = index.as_query_engine(
    include_text=False, response_mode="tree_summarize"
)

response = query_engine.query("Tell me more about Interleaf")