from pathlib import Path
import re
from typing import Tuple, Dict, TextIO
from langchain_core.documents import Document
import tiktoken
from data_ingestion_config import INPUT_ROOT, MODEL_NAME


class TextProcessor:

    def __init__(self):
        self.META_PATTERN = re.compile(r"^(filename|repo_name|rel_path|source_type):\s*(.*)$")



    def process_documents(self, file_root: Path = INPUT_ROOT) -> list[Document]:
        documents_to_embed = []

        for file in file_root.rglob("*"):
            if not file.is_file():
                continue

            content, metadata = self.read_file_and_return_text(file)

            text_chunks = self.chunk_text_from_file(content)
            documents_from_single_file = self.create_documents_from_chunks(text_chunks, metadata)

            documents_to_embed.extend(documents_from_single_file)

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
                match = self.META_PATTERN.match(stripped)
                if match:
                    key, value = match.groups()
                    metadata[key] = value.strip()
                    continue

                if stripped == "":  # ignore blank lines
                    continue

                in_header_metadata_block = False # header block ended

            if stripped == "Scenario:":
                seen_first_scenario = True

            # only extract Meta information for the whole story until first Scenario is seen
            if not file_meta_extracted and not seen_first_scenario:
                if stripped == "Meta:":
                    in_file_meta_block = True
                    continue

                if in_file_meta_block:
                    # End file meta block only when a new main section starts
                    if stripped in ("Scenario:", "Narrative:"):
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


    
    def chunk_text_from_file(self, content) -> list[str]:
        text_chunks = [] 

        in_header = False
        in_scenario = False

        num_tokens = self.count_tokens_from_text(content, MODEL_NAME)
        if num_tokens <= 256:
            text_chunks.append(content)
            return text_chunks

        lines = content.split("\n")

        chunk_header_lines = []
        in_header = False
        header_end_index = 0

        for i, line in enumerate(lines):
            stripped = line.strip()

            if stripped == "Feature:" or stripped == "Narrative:":
                in_header = True
                chunk_header_lines.append(stripped)
                continue

            if in_header:
                if stripped == "Scenario:":
                    header_end_index = i
                    break
                chunk_header_lines.append(stripped)

        chunk_header = "\n".join(chunk_header_lines).strip()

        # collect scenario lines into chunks, each starting with the header
        current_chunk_lines = []
        in_scenario = False

        for line in lines[header_end_index:]:
            stripped = line.strip()

            if stripped == "Scenario:":
                if current_chunk_lines: # when the list is not empty a chunk gets created and added 
                    chunk = f"{chunk_header}\n" + "\n".join(current_chunk_lines).strip()
                    text_chunks.append(chunk)
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

        return text_chunks
    
    
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
    
    def count_tokens_from_text(text: str, model_name: str = MODEL_NAME) -> int:
        encoding = tiktoken.encoding_for_model(model_name)
        num_tokens = len(encoding.encode(text))
        return num_tokens
    
