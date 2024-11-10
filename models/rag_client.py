from qdrant_client import QdrantClient, models
from qdrant_client.http.models import PointStruct
from tqdm import tqdm
import pandas as pd
import time

from models.embedder_client import SentenceEmbedder
from models.openai_client import OpenAIClient
from helpers import read_config, singleton, extract_json_content


config = read_config()
RAG_PROMPT_IN = "The top matching opinions to the user input are: \n"
RAG_PROMPT_END = f"""Return only the opinions' ids that convey the same idea as the user query. Your response should contain only the opinion ids. 
We want to find the opinions that are similar to the user query. First write the opinion id then how similar or dissimilar you think it is. After doing that for all the opinions, write a json object with the opinion ids that are similar to the user query encapsulated with a code block. E.g.:
```json
[1, 2, 3]```
"""
@singleton
class MyQdrantClient:
    def __init__(self, config):
        self.client = QdrantClient("localhost", port=6333)
        self.encoder = SentenceEmbedder(config)
        self.open_ai_model = OpenAIClient(**config["openai"])
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
        hits_data = []
        for hit in hits:
            text = hit.payload["Document"]
            rag_data += f"Opnion_id: {hit.id}. Text: {text} \n"
            hits_data.append({"hit_id": hit.id, "text": text, "topic": hit.payload["Topic"]})
        rag_data += RAG_PROMPT_END
        return {"rag_data": rag_data, "hits": hits_data}

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
            return None
        print(f"Time taken to search: {time.time() - start_time}")
        rag_data = self.get_rag_data(hits)
        print(rag_data)
        try:
            reranked_rag = self.rerank_rag(rag_data["rag_data"])
            all_hits = rag_data["hits"]
            selected_hits = []
            if reranked_rag and all_hits:
                for hit in all_hits:
                    if hit["hit_id"] in reranked_rag:
                        selected_hits.append(hit)
                return selected_hits
            else:
                return None
        except Exception as e:
            print(f" ERROR: Error while re-ranking in OpenAI.\n", e)
            return None
         
    def rerank_rag(self, rag_data):
        messages = [{"role": "user", "content": rag_data}]
        response = self.open_ai_model.off_generate(messages)
        ranked = extract_json_content(response)
        print("ranked ids: ", ranked)
        if ranked and type(ranked) == list:
            return ranked
        else:
            return None


if __name__ == "__main__":
    ########## Create  a Collection ##########
    # client = MyQdrantClient(config)
    # client.create_a_collection(collection_name="polis-fi", vector_size=1024)

    ########## Insert Data ##########
    # df = pd.read_csv("data/global_topic_google_labeled_w_issue_labels.csv")
    # client = MyQdrantClient(config)
    # embedder = SentenceEmbedder(config)
    # for index, row in tqdm(df.iterrows(), total=len(df)):
    #     vector = embedder.get_embeddings(row['Document'])        
    #     client.insert_data(collection_name="polis-fi", id=index, vector=vector, payload=row.to_dict())
    ######### Query Data ##########
    client = MyQdrantClient(config)
    query = "Taxes should be imposed more on companies than on individuals."
    hits = client.get_top_matches_by_query(query)
    print(hits)