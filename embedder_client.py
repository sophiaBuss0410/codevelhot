from helpers import read_config

from sentence_transformers import SentenceTransformer
import torch

config = read_config()

class SentenceEmbedder:
    def __init__(self, config) -> None:
        self.device = "torch" if torch.cuda.is_available() else "cpu"
        self.model = SentenceTransformer(config[""], trust_remote_code=True).to(self.device)

    def get_embeddings(self, text):
        return self.model.encode(text, convert_to_tensor=True).cpu().numpy()
    
