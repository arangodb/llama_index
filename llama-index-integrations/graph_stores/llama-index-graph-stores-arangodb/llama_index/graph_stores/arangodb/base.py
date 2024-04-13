"""ArangoDB graph store implementation."""
NODE_COLLECTION_NAME = 'nodes'
EDGE_COLLECTION_NAME = 'edges'
NODE_TYPE = "ENTITY"
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
        self._arangodb_host = arangodb_host
        self._username = username
        self._password = password
        self._database = database
        self._client = None
        self._db_handle = None
        self._node_collection = None
        self._edge_collection = None
        try:
            self._client =  ArangoClient(hosts=self._arangodb_host)
        except:
            print("Error connecting to ArangoDB. ")
            raise Exception("Error connecting to ArangoDB")
       
        # Check of database exists
        try:
            self._db_handle = self._client.db(self._database, username=self._username, password=self._password)
        except:
            print("Database not found. Please ensure the specified database exits and it accesible by the provided user.")
            raise Exception("Error connecting to speficied Database")
        
        # Create a node and edge collection
        try:
            # Create/Find node collection
            if self._db_handle.has_collection(NODE_COLLECTION_NAME):
                self._node_collection = self._db_handle.collection(NODE_COLLECTION_NAME)
            else:
                self._node_collection = self._db_handle.create_collection(NODE_COLLECTION_NAME)
                
            if self._db_handle.has_collection(EDGE_COLLECTION_NAME):
                self._edge_collection = self._db_handle.collection(EDGE_COLLECTION_NAME)
            else:
                # TODO: Consider making this an actual edge collection edge=True
                self._edge_collection = self._db_handle.create_collection(EDGE_COLLECTION_NAME, edge=True)
        except Exception as inst:
            print("Error finding or creating the required node/edge collections.")
            raise Exception("Error finding or creating the required node/edge collections." + inst)
        
    #  client: Any: The client used to connect to the graph store.
    @property
    def client(self) -> Any:
        return self._client


    #  get: Callable[[str], List[List[str]]]: Get triplets for a given subject.
    def get(self, subj: str) -> List[List[str]]:
        
        res : List[List[str]] = []
        
        # Find all direct neigbhours 
        cursor = self._db_handle.aql.execute("FOR n IN " +  NODE_COLLECTION_NAME + "  FILTER n._key == '" +subj +  "' FOR v,e IN 1..1 OUTBOUND n "+EDGE_COLLECTION_NAME+" RETURN { node: v._key , edge: e.type }")
        for ngh in cursor: 
            res.append([ngh['edge'], ngh['node']])
           
        return res
   
   
    #   get_rel_map: Callable[[Optional[List[str]], int], Dict[str, List[List[str]]]]:
    #        Get subjects' rel map in max depth.
    def get_rel_map(
        self, subjs: Optional[List[str]] = None, depth: int = 2, limit: int = 30
    ) -> Dict[str, List[List[str]]]:
        # Format:
        # {'Node1': [['REL1', 'Node2'],
        # ['REL1', 'Node3'],
        # ['REL1', 'Node3', 'REL1', 'Node4']]}
        
        rel_map: Dict[Any, List[Any]] = {}
        
        if subjs is None or len(subjs) == 0:
            return rel_map
        
        rel_map[subjs[0]] = []
        
        #TODO: right now we only handle the subj in the list (as this is the main use case), can wrap into one more loop.
        
        query = "FOR n IN  " +  NODE_COLLECTION_NAME + " FILTER n._key == '" + subjs[0] +  "' FOR v,e,p IN 1.."+str(depth)+" OUTBOUND n edges RETURN p"
        cursor = self._db_handle.aql.execute(query)
        for path in cursor: 
            # Slice of first element as it is the start node
            vertex_list = path["vertices"][1:]
            
            edges_list  = path["edges"]
           
            path_list = []
            for e, v in zip(edges_list, vertex_list):
                path_list.append(e['type'])
                path_list.append(v['_key'])
            rel_map[subjs[0]].append(path_list)
        
        return rel_map
       
       
    #   upsert_triplet: Callable[[str, str, str], None]: Upsert a triplet.
    def upsert_triplet(self, subj: str, rel: str, obj: str) -> None:
        
        # upsert subject
        _subj = self._node_collection.insert({'_key': subj, 'type' : NODE_TYPE }, overwrite_mode='update')
        
        # upsert object
        _obj = self._node_collection.insert({'_key': obj, 'type' : NODE_TYPE }, overwrite_mode='update')
        
        # upsert edge
        _edg = self._edge_collection.insert({'_key': subj+obj+rel  ,  "_from": str(_subj['_id']) , "_to": str(_obj['_id']), 'type' : rel }, overwrite_mode='update')

        return None
    
    
    #  delete: Callable[[str, str, str], None]: Delete a triplet.
    def delete(self, subj: str, rel: str, obj: str) -> None:
       
        self._edge_collection.delete(subj+obj+rel)
       
        #Todo delete dangling nodes
        
        return None
    
    
    #   get_schema: Callable[[bool], str]: Get the schema of the graph store.
    def get_schema(self, refresh: bool = False) -> str:
        # 'Node properties are the following:\nEntity {id: STRING}\nRelationship properties are the following:\n\nThe relationships are the following:\n(:Entity)-[:REL1]->(:Entity)'
    
        # Currently there is only a single Entity typoe
        node_property_str = "Node properties are the following:\nEntity {id: STRING}\n"
       
        # Edge property
        edge_property_str = "Relationship properties are the following:\n\nThe relationships are the following:\n" 
        # Format: (:Entity)-[:REL1]->(:Entity)'
        cursor = self._db_handle.aql.execute("FOR e IN edges RETURN DISTINCT e.type")
        for rel in cursor: 
            edge_property_str += ("(:Entity)-[:" + rel + "]->(:Entity)\n")
            
        return (node_property_str + edge_property_str)