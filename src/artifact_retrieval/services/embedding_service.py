import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from artifact_retrieval.config.config import MAX_INPUT_SIZE
import logging
import time
from artifact_retrieval.utils.token_counter import TokenCounter

class EmbeddingService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        load_dotenv()
        self.azure_endpoint = os.environ.get("AZURE_ENDPOINT")
        self.api_key = os.environ.get("API_KEY")
        self.deployment_name = os.environ.get("EMBEDDING_DEPLOYMENT_NAME")
        self.embedding_model = self.initialize_embedding_model()
    
    # creates an instance of the OpenAIEmbeddings to be consistent for retrieval and ingestion
    def initialize_embedding_model(self):
        return OpenAIEmbeddings(
        model=self.deployment_name,
        base_url=self.azure_endpoint,
        api_key=self.api_key,
        check_embedding_ctx_length=False,
        )
    
    def generate_embeddings_for_documents(self, documents: list[str]) -> list[list[float]]:
        all_embeddings = []
        document_batches = self.prepare_batches_based_on_token_count(documents)

        self.logger.info(f"Generating embeddings for {len(documents)} documents splitted into {len(document_batches)} batches.")

        for document_batch in document_batches:
            embeddings= self.embedding_model.embed_documents(document_batch)
            all_embeddings.extend(embeddings)
            time.sleep(0.2) # little delay, avoid hitting rate limits --> 1 mil tokens per minute allowed
            # self.logger.info(f"Generated embeddings for batch of {len(document_batch)} documents.")

        self.logger.info(f"Total embeddings generated: {len(all_embeddings)}")  
        return all_embeddings

    def prepare_batches_based_on_token_count(self, documents: list [str]) -> list[list[str]]:
        token_counter = TokenCounter()

        document_batches = []
        current_batch = []
        current_tokens = 0

        for document in documents:
            document_tokens = token_counter.count_tokens_from_text(document)

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