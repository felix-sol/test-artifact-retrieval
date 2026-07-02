from pathlib import Path
import re
from typing import Tuple, Dict, TextIO
from langchain_core.documents import Document
import tiktoken
from data_ingestion.config.data_ingestion_config import INPUT_ROOT, MODEL_NAME
import logging


class TextProcessor:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.META_PATTERN = re.compile(r"^(filename|repo_name|rel_path|source_type):\s*(.*)$")
        self.counter_not_chunked = 0
        self.counter_chunked = 0
        self.chunks_total = list()
        self.FEATURE_RE = re.compile(r"^\s*Feature:")
        self.SCENARIO_RE = re.compile(r"^\s*Scenario:")
        self.NARRATIVE_RE = re.compile(r"^\s*Narrative:")
        self.SECTION_RE = re.compile(r"^\s*(Narrative|Scenario|):")

    # pipeline method to process all documents in a directory, returning a list of LangChain Document objects
    def process_documents(self, file_root: Path = INPUT_ROOT) -> list[Document]:
        documents_to_embed = []
        counter = 0
        for file in file_root.rglob("*"):
            if not file.is_file():
                continue

            counter += 1

            with open(file, "r", encoding="utf-8") as f:
                content, metadata = self.read_file_and_return_text(f)

            text_chunks = self.chunk_text_from_file(content)
            documents_from_single_file = self.create_documents_from_chunks(text_chunks, metadata)
            documents_to_embed.extend(documents_from_single_file)

        self.logger.info(f"Processed {counter} files in total.")
        self.logger.info(f"Number of documents not to chunk: {self.counter_not_chunked}")
        self.logger.info(f"Number of documents to chunk: {self.counter_chunked}")
        self.logger.info(f"Total number of chunks created from documents larger than 256 Tokens: {len(self.chunks_total)}")
        self.logger.info(f"Created {len(documents_to_embed)} LangChain documents based on text chunks from directory '{file_root}'.")
        self.logger.info(f"{self.counter_not_chunked + len(self.chunks_total)} documents processed in total.")
        
        return documents_to_embed
    

    # extracts the text and metadata from a file, returning both as a tuple
    def read_file_and_return_text(self, file: TextIO) -> Tuple[str, Dict[str, str]]:
        metadata = {}
        content_lines = []

        in_header_metadata_block = True
        in_file_meta_block = False
        file_meta_extracted = False
        seen_first_scenario = False

        for line in file:
            stripped = line.rstrip("\n")

            # Extract initial technical metadata block annotated with "metadata:" at the top of each file
            if in_header_metadata_block:
                if stripped.startswith("metadata:"):
                    continue  # skip the metadata header line
                match = self.META_PATTERN.match(stripped)
                if match:
                    key, value = match.groups()
                    metadata[key] = value.strip()
                    continue

                if stripped == "":  # ignore blank lines
                    continue

                in_header_metadata_block = False # header block ended

            if self.SCENARIO_RE.match(stripped):
                seen_first_scenario = True

            # only extract Meta information for the whole story until first Scenario is seen
            if not file_meta_extracted and not seen_first_scenario:
                if stripped == "Meta:":
                    in_file_meta_block = True
                    continue

                if in_file_meta_block:
                    # End file meta block only when a new main section starts
                    if self.SECTION_RE.match(stripped):
                        in_file_meta_block = False
                        file_meta_extracted = True
                        content_lines.append(stripped)
                        continue

                    if stripped == "":
                        continue

                    if "file_meta" not in metadata:
                        metadata["file_meta"] = []
                    metadata["file_meta"].append(stripped)
                    continue

            content_lines.append(stripped) # keep everything else as content

        file.close()

        # adjust content and metadata before returning
        content = "\n".join(content_lines).strip()
        if "file_meta" in metadata:
            metadata["file_meta"] = "\n".join(metadata["file_meta"])

        return content, metadata


    # chunks documents based on the presence of Scenario annotations above the threshold of 256 tokens
    def chunk_text_from_file(self, content) -> list[str]:
        text_chunks = [] 

        in_header = False
        in_scenario = False

        num_tokens = self.count_tokens_from_text(content, MODEL_NAME)
        if num_tokens <= 256:
            text_chunks.append(content)
            self.counter_not_chunked += 1
            return text_chunks # small files are not chunked, treated as a single chunk

        self.counter_chunked += 1
        lines = content.split("\n")

        chunk_header_lines = []
        in_header = False
        header_end_index = 0

        for i, line in enumerate(lines):
            stripped = line.strip()

            if self.FEATURE_RE.match(stripped) or self.NARRATIVE_RE.match(stripped):
                in_header = True
                chunk_header_lines.append(stripped)
                continue

            if in_header:
                if self.SCENARIO_RE.match(stripped):
                    header_end_index = i
                    break
                chunk_header_lines.append(stripped)

        chunk_header = "\n".join(chunk_header_lines).strip()

        # collect scenario lines into chunks, each starting with the header
        current_chunk_lines = []
        in_scenario = False

        for line in lines[header_end_index:]:
            stripped = line.strip()

            if self.SCENARIO_RE.match(stripped): 
                if current_chunk_lines: # when the list is not empty a chunk gets created and added 
                    chunk = f"{chunk_header}\n" + "\n".join(current_chunk_lines).strip()
                    text_chunks.append(chunk)
                    self.chunks_total.append(chunk)
                    current_chunk_lines = []

                in_scenario = True
                current_chunk_lines.append(stripped)
                continue

            if in_scenario:
                current_chunk_lines.append(stripped)

        # append last chunk if any lines are left
        if current_chunk_lines:
            chunk = f"{chunk_header}\n" + "\n".join(current_chunk_lines).strip()
            text_chunks.append(chunk)
            self.chunks_total.append(chunk)

        return text_chunks
    
    # creates LangChain Document objects from text chunks and attaches metadata to each document
    def create_documents_from_chunks(self, chunks, metadata) -> list[Document]:
        documents_from_chunks = []

        for chunk in chunks:
            documents_from_chunks.append(
                Document(
                    page_content=chunk,
                    metadata=metadata
                )
            )

        return documents_from_chunks
    
    # counts number of tokens in a text
    @staticmethod
    def count_tokens_from_text(text: str, model_name: str = MODEL_NAME) -> int:
        encoding = tiktoken.encoding_for_model(model_name)
        num_tokens = len(encoding.encode(text))
        return num_tokens
    
