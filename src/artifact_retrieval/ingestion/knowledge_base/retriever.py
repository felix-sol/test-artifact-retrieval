from artifact_retrieval.config.config import setup_logging
from artifact_retrieval.ingestion.knowledge_base.config.knowledge_base_config import COLLECTION
from artifact_retrieval.ingestion.knowledge_base.database_manager import DatabaseManager
from artifact_retrieval.services.embedding_service import EmbeddingService
import logging


from langchain_qdrant import QdrantVectorStore
from langchain_qdrant import RetrievalMode

class Retriever:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.database_manager = DatabaseManager()
        self.embedding_service = EmbeddingService()
        self.collection_name = COLLECTION
        self.retriever = self.initialize_retriever()


    def create_lang_chain_vector_store(self, collection_name: str) -> QdrantVectorStore:
        embedding_model = self.embedding_service.embedding_model

        vector_store = QdrantVectorStore(
            client=self.database_manager.client,
            collection_name=collection_name,
            embedding=embedding_model,
            retrieval_mode=RetrievalMode.DENSE,

        )
        self.logger.info(f"Vector store created for collection '{collection_name}'.")
        return vector_store


    # needs an existing collection, knowledge base ingestion must have been done before
    def initialize_retriever(self):
        vector_store = self.create_lang_chain_vector_store(self.collection_name)
        self.retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )

        return self.retriever
    

    def retrieve_documents(self, query: str):
        if self.retriever is None:
            raise ValueError("Retriever has not been created yet. ")

        return self.retriever.invoke(query)
    

