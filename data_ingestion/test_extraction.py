from EmbeddingService import EmbeddingService
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import tiktoken

text_splitter = RecursiveCharacterTextSplitter(chunk_size=2800, chunk_overlap=0)


# Funktion, um den Inhalt eines Dokuments zu lesen
def read_document_and_return_chunks(file):
    content = ""
    line = file.readline()
    while line:
            content += line.strip() + " "
            line = file.readline()
    file.close()
    print(f"length of content: {len(content)}\n")
    print(f"Number of Tokens: {num_tokens_from_string(content, 'cl100k_base')}\n")
    chunks = text_splitter.split_text(content)
    return chunks


def create_documents_from_chunks(chunks, source):
    documents = []
    for chunk in chunks:
        documents.append(
            Document(
                page_content=chunk,
                metadata={"source": source}
            )
        )        
    return documents

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens





source_1 = "data_ingestion/sample_data/sample_story.story"
source_2 = "data_ingestion/sample_data/sample.txt"
chunks_content_1 = read_document_and_return_chunks(open(source_1, "r"))
chunks_content_2 = read_document_and_return_chunks(open(source_2, "r"))


documents_list_from_splitter = text_splitter.create_documents(
    chunks_content_1,
    [{"source": source_1}] * len(chunks_content_1)
)
for documents in documents_list_from_splitter:
     print(f"Document from {documents.metadata['source']} with content: {documents.page_content}...\n")

documents_1 = create_documents_from_chunks(chunks_content_1, source_1)
#documents_2 = create_documents_from_chunks(chunks_content_2, source_2)

for documents in documents_1:
     print(f"Document from {documents.metadata['source']} with content: {documents.page_content}...\n")

#for documents in documents_2:
#     print(f"Document from {documents.metadata['source']} with content: {documents.page_content}...\n")






# kombinieren der Chunk Listen in eine
#documents = documents_1 + documents_2



# Embedding Modell callen und Vektoren generieren
#embeddings = EmbeddingService()
#vector_1 = embeddings.generate_query_embedding(documents[0].page_content)
#vector_2 = embeddings.generate_query_embedding(documents[1].page_content)

#assert len(vector_1) == len(vector_2)
#print(f"Generated vectors of length {len(vector_1)}\n")
#print(vector_1[:10])
