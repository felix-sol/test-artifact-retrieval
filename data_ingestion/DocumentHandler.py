
from qdrant_client.models import PointStruct

from EmbeddingService import EmbeddingService
from data_ingestion.TextProcessor import TextProcessor
from config import setup_logging
from data_ingestion.config.data_ingestion_config import INPUT_ROOT
from knowledge_base.DatabaseManager import DatabaseManager
import logging


class DocumentHandler:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.root_dir = INPUT_ROOT
        self.text_processor = TextProcessor()
        self.embedding_service = EmbeddingService()
        self.database_manager = DatabaseManager()  

    # pipeline that triggers the creation of LangChain Documents, their embeddings, and the storage of the full object in Qdrant
    def ingest_knowledge_base(self):
        documents_to_embed, embeddings = self.embed_documents_from_directory()

        if not documents_to_embed:
            self.logger.warning("No documents found to embed.")
            return
        
        if not embeddings:
            self.logger.warning("No embeddings generated.")
            return
        self.logger.info(f"Number of documents embedded: {len(documents_to_embed)}")
        self.store_full_object_in_qdrant(documents_to_embed, embeddings)
        self.logger.info("Knowledge base ingestion completed successfully.")



    # turns documents into a list to hand to the EmbeddingService and returns the embeddings
    def embed_documents_from_directory(self):
        documents_to_embed = self.text_processor.process_documents(self.root_dir)
        self.logger.info(f"Number of Documents to embed: {len(documents_to_embed)}")

        # copy of the page content to only embed the text and not the metadata
        contents = [doc.page_content for doc in documents_to_embed]
        self.logger.info(f"Number of page contents extracted: {len(contents)}")

        embeddings = self.embedding_service.generate_embeddings_for_documents(contents)
        return documents_to_embed, embeddings # both needed for an entry in vector database


    def store_full_object_in_qdrant(self, documents_to_embed, embeddings):
        if len(documents_to_embed) != len(embeddings):
            raise ValueError(
                f"Mismatch: {len(documents_to_embed)} documents but {len(embeddings)} embeddings."
                )

        collection_name = "knowledge_base"

        if self.database_manager.client.collection_exists(collection_name):
            self.logger.info(f"Collection '{collection_name}' already exists. Removing it for a fresh start.")
            self.database_manager.client.delete_collection(collection_name)
        
        # create collection in Qdrant with the appropriate vector size
        self.database_manager.create_collection(
            collection_name, 
            vector_size=len(embeddings[0]))

        # combine original chunks with their embeddings into PointStruct objects for upsert into Qdrant
        points = [
            PointStruct(
                id=index,
                vector=embedding,
                payload={
                    "content": document.page_content,
                    **document.metadata,
                },
            )
            for index, (document, embedding) in enumerate(zip(documents_to_embed, embeddings))
        ]

        self.database_manager.upsert_points_in_batches(
            collection_name=collection_name,
            points=points,
        )
        self.logger.info(f"Points upserted into collection '{collection_name}' successfully.")


def main() -> None:
    setup_logging()
    document_handler = DocumentHandler()
    document_handler.ingest_knowledge_base()

if __name__ == "__main__":
    main()    
    

    


   