from config import setup_logging
from knowledge_base.config.knowledge_base_config import COLLECTION
from knowledge_base.DatabaseManager import DatabaseManager
from EmbeddingService import EmbeddingService
import logging


from langchain_qdrant import QdrantVectorStore
from langchain_qdrant import RetrievalMode

class Retriever:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.database_manager = DatabaseManager()
        self.embedding_service = EmbeddingService()
        self.collection_name = COLLECTION
        self.retriever = None


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
    def create_retriever(self):
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
    

def main():
    setup_logging()
    retriever = Retriever()
    retriever.create_retriever()
    # sample query
    results = retriever.retrieve_documents("How is The Scenario \"The filter popup of the activity dialog does not appear behind the clipboard\" implemented?")
    print(results[0])
    print(results[1])

if __name__ == "__main__":
    main()

