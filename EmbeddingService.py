import os
from dotenv import load_dotenv
from openai import OpenAI
import logging

class EmbeddingService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        load_dotenv()
        self.azure_endpoint = os.environ.get("AZURE_ENDPOINT")
        self.api_key = os.environ.get("API_KEY")
        self.model_name = os.environ.get("EMBEDDING_MODEL_NAME")

        

    def generate_embeddings(self, inputs):
        client = OpenAI(
            base_url=self.azure_endpoint,
            api_key=self.api_key,
        )

        embedding_response = client.embeddings.create(
            model=self.model_name,
            input=inputs,
            encoding_format="float"
        )

        self.logger.info(f"Generated embeddings for {len(inputs)} inputs.")
        self.logger.info(f"Total tokens consumed for embedding generation: {embedding_response.usage.total_tokens}")
        return [item.embedding for item in embedding_response.data]
    

    def generate_query_embedding(self, content: str) -> list[float]:
        self.logger.info("Generating query embedding.")
        return self.generate_embeddings(content)[0]
    
    def generate_embeddings_for_documents(self, documents: list[str]) -> list[list[float]]:
        self.logger.info(f"Generating embeddings for {len(documents)} documents.")
        return self.generate_embeddings(documents)

    
    

    
    
    
