from qdrant_client import QdrantClient, models
from qdrant_client.http.models import PointStruct
from tqdm import tqdm
import pandas as pd

from embedder_client import SentenceEmbedder
from helpers import read_config, singleton


config = read_config()

@singleton
class MyQdrantClient:
    def __init__(self, config):
        self.client = QdrantClient("localhost", port=6333)
        self.encoder = SentenceEmbedder(config)
        self.collection_name = config["rag"]["collection_name"] 
        self.score_threshold = config["rag"]["score_threshold"]
        self.max_search_limit = config["rag"]["max_search_limit"]
        self.qdrant_timeout = config["rag"]["qdrant_timeout"]

    def create_a_collection(self, collection_name, vector_size):
        self.client.create_collection(
            collection_name=f"{collection_name}",
            vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
        )

    def insert_data(self, collection_name, id, vector, payload):
        operation_info = self.client.upsert(
        collection_name=collection_name,
        wait=True,
        points=[
            PointStruct(id=id, vector=vector, payload=payload)
        ],
        )
        print(operation_info)

    def get_top_matches_by_query(self, query: str):
        vector = self.encoder.get_embeddings(query).tolist()
        search_dict = {"collection_name": self.collection_name,
                        "query_vector": vector,
                        "limit": self.max_search_limit ,
                        "score_threshold": self.score_threshold,
                        "timeout": self.qdrant_timeout
                        }
        
        try:
            hits = self.client.search(
                **search_dict
            )
        except Exception as e:
            print( f" ERROR: Error while searching in Qdrant.\n", e)

        return hits



if __name__ == "__main__":

    ########## Query Data ##########
    client = MyQdrantClient(config)
    query = "What is the capital of Finland?"
    hits = client.get_top_matches_by_query(query)
    print(hits)

    ########## Create  a Collection ##########
    # client = MyQdrantClient()
    # client.create_a_collection(collection_name="polis-fi", vector_size=1024)

    ########## Insert Data ##########
    # df = pd.read_csv("data/topics_google_four.csv")
    # client = MyQdrantClient()
    # embedder = SentenceEmbedder(config)
    # for index, row in tqdm(df.iterrows(), total=len(df)):
    #     vector = embedder.get_embeddings(row['txt_en'])        
    #     client.insert_data(collection_name="polis-fi", id=index, vector=vector, payload=row.to_dict())