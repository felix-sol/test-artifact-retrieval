import logging
import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate 

from artifact_retrieval.utils.prompts.system_prompts import RAG_SYSTEM_PROMPT

class LLMService:

    def __init__(self):   
        self.logger = logging.getLogger(__name__) 
        load_dotenv()
        self.azure_endpoint = os.environ.get("AZURE_ENDPOINT")
        self.api_key = os.environ.get("API_KEY")
        self.deployment_name = os.environ.get("LLM_DEPLOYMENT_NAME")
        self.llm = self.initialize_chat_model()
        self.system_prompt = RAG_SYSTEM_PROMPT 


    def initialize_chat_model(self):
        return ChatOpenAI(
            model=self.deployment_name,
            base_url=self.azure_endpoint,
            api_key=self.api_key,
            temperature=0.6,
            top_p=0.95,
            max_tokens=2048, 
            timeout=60,
            max_retries=2,
        )
    
    def generate_response(self, documents: list, query: str) -> str:
        context_parts = []

        for i, document in enumerate(documents, start=1):
            metadata_text = "\n".join(f"{key}: {value}" for key, value in document.metadata.items())

            context_parts.append(
                f"---Retrieved document {i} ---\n"
                f"METADATA:\n{metadata_text}\n\n" 
                f"CONTENT:\n{document.page_content}\n\n"
                f"--- End retrieved document {i} ---"
            )

        context = "\n\n".join(context_parts)    

        if not context:
            self.logger.warning("No documents retrieved. Proceeding with an empty context.")
            context = "No relevant documents were retrieved."

        template = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                ("human", "Retrieved Context:\n{context}\n\n Query:\n{query}"),
            ]
        )

        messages = template.format_messages(context=context, query=query)
        self.logger.info(f"calling LLM with query '{query}' and context length {len(context)} and metadata")
        response = self.llm.invoke(messages).content # only returns textual response of the model, adjust if more than the text is needed
        return response

