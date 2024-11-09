from qdrant_client import QdrantClient, models
from qdrant_client.http.models import PointStruct
from tqdm import tqdm
import pandas as pd
import time

from models.embedder_client import SentenceEmbedder
from helpers import read_config, singleton


config = read_config()
RAG_PROMPT_IN = "The top matching opinions to the user input are: \n"
RAG_PROMPT_END = f"""Return only the opinions' ids that convey the same idea as the user query. Your response should contain only the opinion ids. 
We want to find the opinions that are similar to the user query. First write the opinion id then how similar or dissimilar you think it is. After doing that for all the opinions, write a json object with the opinion ids that are similar to the user query encapsulated with a code block. E.g.:
```json
[1, 2, 3]
```
"""
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

    def get_rag_data(self, hits):
        rag_data = RAG_PROMPT_IN
        for hit in hits:
            text = hit.payload["txt_en"]
            rag_data += f"Opnion_id: {hit.id}. Text: {text} \n"
        rag_data += RAG_PROMPT_END
        return rag_data

    def get_top_matches_by_query(self, query: str):
        start_time = time.time()
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
        print(f"Time taken to search: {time.time() - start_time}")
        return hits



if __name__ == "__main__":

    ########## Create  a Collection ##########
    # client = MyQdrantClient(config)
    # client.create_a_collection(collection_name="polis-fi", vector_size=1024)

    ########## Insert Data ##########
    # df = pd.read_csv("data/global_topic_google.csv")
    # client = MyQdrantClient(config)
    # embedder = SentenceEmbedder(config)
    # for index, row in tqdm(df.iterrows(), total=len(df)):
    #     vector = embedder.get_embeddings(row['txt_en'])        
    #     client.insert_data(collection_name="polis-fi", id=index, vector=vector, payload=row.to_dict())


    ########## Query Data ##########
    client = MyQdrantClient(config)
    query = "Taxes should be more on companies than on individuals."
    hits = client.get_top_matches_by_query(query)
    print(client.get_rag_data(hits))