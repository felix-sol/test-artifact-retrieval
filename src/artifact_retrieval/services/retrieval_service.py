import logging
from artifact_retrieval.services.llm_service import LLMService
from artifact_retrieval.config.config import setup_logging
from artifact_retrieval.ingestion.knowledge_base.retriever import Retriever

# central service which orchestrates the RAG pipeline
# sets up retrieval of needed documents, augmentation of prompt and generation of the final response
class RetrievalService:
    
    def __init__(self, retriever: Retriever, llm_service: LLMService):
        self.logger = logging.getLogger(__name__)
        self.retriever = retriever
        self.llm_service = llm_service
        

    def retrieve_and_generate_response(self, query: str) -> tuple[str, list[dict]]:
        documents = self.retriever.retrieve_documents(query)   
        self.logger.info(f"documents retrieved for query '{query}': {len(documents)}")

        sources_by_key = {}

        for doc in documents:
            metadata = doc.metadata

            source_key = (metadata.get("filename"), metadata.get("repo_name"), metadata.get("rel_path"), metadata.get("source_type"))

            if source_key not in sources_by_key:
                sources_by_key[source_key] = {
                    "filename": metadata.get("filename"),
                    "repo_name": metadata.get("repo_name"),
                    "rel_path": metadata.get("rel_path"),
                    "source_type": metadata.get("source_type"),
                    "chunk_count": 1,
                }
            else:
                sources_by_key[source_key]["chunk_count"] += 1

        sources = list(sources_by_key.values())

        #TODO  Reranker call 

        response = self.llm_service.generate_response(documents, query)
        self.logger.info(f"response generated")
        return response, sources
