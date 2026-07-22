import logging
import os
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
            model_name=self.deployment_name,
            base_url=self.azure_endpoint,
            api_key=self.api_key,
            temperature=0,
            max_tokens=None, # optimize parameters
            timeout=None,
            max_retries=2,
        )
    
    def generate_response(self, content: str, metadata: dict, query: str) -> str:
        #TODO: implementieren der Methode zum chatten, ggf. mit Chat History, schauen, wie metadaten behandeln
        template = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                ("human", "Context: {content}\n\n Metadata: {metadata}\n\n Query: {query}"),
            ]
        )

        messages = template.format_messages(content=content, metadata=metadata, query=query)
        self.logger.info(f"calling LLM with query '{query}' and content length {len(content)} and metadata {metadata}")
        response = self.llm.invoke(messages).content # only returns textual response of the model, adjust if more than the text is needed
        return response

