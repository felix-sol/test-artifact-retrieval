import os
from dotenv import load_dotenv
from openai import OpenAI

class EmbeddingService:

    def __init__(self):
        load_dotenv()
        self.azure_endpoint = os.environ.get("AZURE_ENDPOINT")
        self.api_key = os.environ.get("API_KEY")
        self.model_name = os.environ.get("EMBEDDING_MODEL_NAME")

    
    def generate_query_embedding(self, content):
        client = OpenAI(
            base_url=self.azure_endpoint,
            api_key=self.api_key,
        )

        embedding_response = client.embeddings.create(
            model=self.model_name,
            input=content,
            encoding_format="float"
        )
        client.embeddings.batch.create

        return(embedding_response.data[0].embedding)
    
    
    
    
