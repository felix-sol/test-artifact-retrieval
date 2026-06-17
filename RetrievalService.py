from Embedding_Service import EmbeddingService
from LLM_Service import LLMService


class RetrievalService:
    
    query = "What is the capital of Australia?"

    LLM = LLMService()
    Embedder = EmbeddingService()

    llm_result =LLM.generate_response(query)
    embedding =Embedder.generate_query_embedding(query)
    print("LLM Result: ", llm_result)
    print("Embedding: ", embedding)