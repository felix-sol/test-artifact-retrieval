from fastapi import FastAPI
from contextlib import asynccontextmanager
from artifact_retrieval.application.backend.api.routers import router
from artifact_retrieval.services.llm_service import LLMService
from artifact_retrieval.services.retrieval_service import RetrievalService
from artifact_retrieval.ingestion.knowledge_base.retriever import Retriever


@asynccontextmanager
async def lifespan(app: FastAPI):
    retriever = Retriever()
    llm_service = LLMService()
    retrieval_service = RetrievalService(retriever, llm_service)

    app.state.retriever = retriever
    app.state.llm_service = llm_service
    app.state.retrieval_service = retrieval_service
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(router.router)



