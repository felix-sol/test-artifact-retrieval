
from qdrant_client.grpc import PointStruct

from EmbeddingService import EmbeddingService
from TextProcessor import TextProcessor
from data_ingestion_config import INPUT_ROOT
from knowledge_base.DatabaseManager import DatabaseManager
import logging


class DocumentHandler:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.root_dir = INPUT_ROOT
        self.text_processor = TextProcessor()
        self.embedding_service = EmbeddingService()
        self.database_manager = DatabaseManager()  


    def ingest_knowledge_base(self):
        documents_to_embed, embeddings = self.embed_documents_from_directory()

        if not documents_to_embed:
            self.logger.warning("No documents found to embed.")
            return
        
        if not embeddings:
            self.logger.warning("No embeddings generated.")
            return
        
        self.store_full_object_in_qdrant(documents_to_embed, embeddings)
        self.logger.info("Knowledge base ingestion completed successfully.")




    def embed_documents_from_directory(self):
        documents_to_embed = self.text_processor.process_documents(self.root_dir)
        contents = [doc.page_content for doc in documents_to_embed]
        embeddings = self.embedding_service.generate_embeddings_for_documents(contents)

        self.logger.info(f"Number of Documents to embed: {len(documents_to_embed)}")
        self.logger.info(f"Number of page contents extracted: {len(contents)}")
        self.logger.info(f"Number of Embeddings generated: {len(embeddings)}")
        return documents_to_embed, embeddings


    def store_full_object_in_qdrant(self, documents_to_embed, embeddings):
        # create collection in Qdrant with the appropriate vector size
        self.database_manager.create_collection(
            collection_name="knowledge_base", 
            vector_size=len(embeddings[0]))

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

        self.database_manager.upsert_points(
            collection_name="knowledge_base",
            points=points
        )
        self.logger.info("Points upserted into collection 'knowledge_base' successfully.")
    

    

    


   