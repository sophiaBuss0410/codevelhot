from qdrant_client import QdrantClient, models






def create_a_collection(collection_name, vector_size):
    client = QdrantClient(url="http://localhost:6333")

    client.create_collection(
        collection_name=f"{collection_name}",
        vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
    )