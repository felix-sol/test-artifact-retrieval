import logging

EMBEDDING_MODEL_NAME = "text-embedding-3-large"
MAX_INPUT_SIZE = 7000 # Model allows up to 8192 Tokens, but leaving some safety buffer

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )