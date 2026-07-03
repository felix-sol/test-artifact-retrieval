import os
from dotenv import load_dotenv
from openai import OpenAI
from config import MAX_INPUT_SIZE
import logging
import time
from TokenCounter import TokenCounter

class EmbeddingService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        load_dotenv()
        self.azure_endpoint = os.environ.get("AZURE_ENDPOINT")
        self.api_key = os.environ.get("API_KEY")
        self.model_name = os.environ.get("EMBEDDING_MODEL_NAME")
        self.tokenCounter = TokenCounter()

        
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

        return [item.embedding for item in embedding_response.data], embedding_response.usage.total_tokens
    

    def generate_query_embedding(self, content: str) -> list[float]:
        self.logger.info("Generating query embedding.")
        return self.generate_embeddings(content)[0]
    
    def generate_embeddings_for_documents(self, documents: list[str]) -> list[list[float]]:
        all_embeddings = []
        total_tokens_used = 0
        document_batches = self.prepare_batches_based_on_token_count(documents)

        self.logger.info(f"Generating embeddings for {len(documents)} documents splitted into {len(document_batches)} batches.")

        for document_batch in document_batches:
            embeddings, tokens_used = self.generate_embeddings(document_batch)
            all_embeddings.extend(embeddings)
            total_tokens_used += tokens_used
            time.sleep(0.2) # little delay, avoid hitting rate limits --> 1 mil tokens per minute allowed
            # self.logger.info(f"Generated embeddings for batch of {len(document_batch)} documents.")

        self.logger.info(f"Total embeddings generated: {len(all_embeddings)}")  
        self.logger.info(f"Total tokens used: {total_tokens_used}")
        return all_embeddings

    def prepare_batches_based_on_token_count(self, documents: list [str]) -> list[list[str]]:
        document_batches = []
        current_batch = []
        current_tokens = 0

        for document in documents:
            document_tokens = self.tokenCounter.count_tokens_from_text(document)

            # if adding current document exceeds context window, current batch gets finalized
            if current_batch and current_tokens + document_tokens > MAX_INPUT_SIZE:
                document_batches.append(current_batch)
                current_batch = []
                current_tokens = 0

            # new one is started with resetted values
            current_batch.append(document)
            current_tokens += document_tokens

        # append the last batch if it has any documents
        if current_batch:
            document_batches.append(current_batch)

        return document_batches

    
    

    
    
    
