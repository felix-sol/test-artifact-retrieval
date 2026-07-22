import tiktoken
from artifact_retrieval.config.config import EMBEDDING_MODEL_NAME


class TokenCounter:
    def __init__(self):
        self.model_name = EMBEDDING_MODEL_NAME
        self.encoding = tiktoken.encoding_for_model(self.model_name)

    def count_tokens_from_text(self, text: str) -> int:
        num_tokens = len(self.encoding.encode(text))
        return num_tokens
    
    