from qdrant_client import QdrantClient, models
from qdrant_client.http.models import PointStruct

from embedder_client import SentenceEmbedder
from helpers import read_json
from tqdm import tqdm

class MyQdrantClient:
    def __init__(self, **kwargs):
        self.client = QdrantClient("localhost", port=6333)

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




if __name__ == "__main__":
    data = read_json("")
    client = MyQdrantClient()
    embedder = SentenceEmbedder()
    for index, d in tqdm(enumerate(data), total=len(data)):
        vector = embedder.get_embeddings(d['input'])
        client.insert_data(collection_name="polis-fi", id=index, vector=vector, payload=d)
        