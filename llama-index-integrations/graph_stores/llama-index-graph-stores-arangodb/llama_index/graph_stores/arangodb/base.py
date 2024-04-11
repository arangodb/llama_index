"""ArangoDB graph store implementation."""
from typing import Any, Dict, List, Optional

from llama_index.core.graph_stores.types import GraphStore

from arango import ArangoClient


"""Abstract graph store protocol.

    This protocol defines the interface for a graph store, which is responsible
    for storing and retrieving knowledge graph data.

    Attributes:
        client: Any: The client used to connect to the graph store.
        get: Callable[[str], List[List[str]]]: Get triplets for a given subject.
        get_rel_map: Callable[[Optional[List[str]], int], Dict[str, List[List[str]]]]:
            Get subjects' rel map in max depth.
        upsert_triplet: Callable[[str, str, str], None]: Upsert a triplet.
        delete: Callable[[str, str, str], None]: Delete a triplet.
        persist: Callable[[str, Optional[fsspec.AbstractFileSystem]], None]:
            Persist the graph store to a file.
        get_schema: Callable[[bool], str]: Get the schema of the graph store.
 """

class ArangoDBGraphStore(GraphStore):
    def __init__(
        self,
        arangodb_host : str = None,
        username : str = None,
        password : str = "_system",
        database : str = None,
        ) -> None:
        self.arangodb_host = arangodb_host
        self.username = username
        self.password = password
        self.database = database
        self.client = None
        try:
            self.client =  ArangoClient(hosts="")
            self.db_handle = client.db(self.databasedatabase, username=self.username, password=self.password)
        except:
            print("Error connecting to ArangoDB")

 
    #  client: Any: The client used to connect to the graph store.
    @property
    def client(self) -> Any:
        return None
        client = ArangoClient(hosts="http://localhost:8529")

    #  get: Callable[[str], List[List[str]]]: Get triplets for a given subject.
    def get(self, subj: str) -> List[List[str]]:
        return None
   
    #   get_rel_map: Callable[[Optional[List[str]], int], Dict[str, List[List[str]]]]:
    #        Get subjects' rel map in max depth.
    def get_rel_map(
        self, subjs: Optional[List[str]] = None, depth: int = 2, limit: int = 30
    ) -> Dict[str, List[List[str]]]:
        return None
       
    #   upsert_triplet: Callable[[str, str, str], None]: Upsert a triplet.
    def upsert_triplet(self, subj: str, rel: str, obj: str) -> None:
        return None
    
    #  delete: Callable[[str, str, str], None]: Delete a triplet.
    def delete(self, subj: str, rel: str, obj: str) -> None:
        return None
    
    #   get_schema: Callable[[bool], str]: Get the schema of the graph store.
    def get_schema(self, refresh: bool = False) -> str:
        return None
    
