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
        

    def retrieve_and_generate_response(self, query: str) -> str:
        documents = self.retriever.retrieve_documents(query)   
        self.logger.info(f"documents retrieved for query '{query}': {len(documents)}")
        #content = "\n\n".join([doc.page_content for doc in documents]) # for all retrieved documents as content to be passed to the LLM
        metadata = [doc.metadata for doc in documents] # for all retrieved documents as metadata to be passed to the LLM

        single_content = documents[0].page_content if documents else "" # only first retrieved document as content to be passed to the LLM
        single_metadata = metadata[0] if metadata else {} # only first retrieved document's metadata to be passed to the LLM
        self.logger.info(f"first extracted document: {single_content}")

        response = self.llm_service.generate_response(single_content, single_metadata, query)
        self.logger.info(f"response generated")
        return response



# def main():
#     setup_logging()
#     retriever = Retriever()
#     llm_service = LLMService()
#     retrieval_service = RetrievalService(retriever, llm_service)
#     query = "How is The Scenario \"The filter popup of the activity dialog does not appear behind the clipboard\" implemented?"

#     response = retrieval_service.retrieve_and_generate_response(query)

#     print(response)


# if __name__ == "__main__":
#     main()    