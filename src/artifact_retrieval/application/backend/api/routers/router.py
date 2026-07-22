from fastapi import APIRouter
from pydantic import BaseModel
from fastapi import Depends
from artifact_retrieval.services.llm_service import LLMService
from artifact_retrieval.services.retrieval_service import RetrievalService
from artifact_retrieval.ingestion.knowledge_base.retriever import Retriever
from artifact_retrieval.application.backend.api.dependencies import get_retrieval_service


router = APIRouter()



@router.get("/")
def root():
    # entry point for the app, Startseite
    return {"Hello": "World"}

@router.get("/health")
def health_check():
    # health check endpoint to check if the service is running
    return {"status": "ok"}


@router.get("/query")
def query_knowledge_base(retrieval_service: RetrievalService = Depends(get_retrieval_service)):
    query = "How is The Scenario \"The filter popup of the activity dialog does not appear behind the clipboard\" implemented?"
    response = retrieval_service.retrieve_and_generate_response(query)
    return {"response": response}

@router.post("/chat")
def chat_with_llm(query:str, retrieval_service: RetrievalService = Depends(get_retrieval_service)):
    response = retrieval_service.retrieve_and_generate_response(query)
    return {"response": response}


@router.get("/download")
def download_chat_history():
    #TODO: implementieren der Methode zum herunterladen der Chat History
    return None

