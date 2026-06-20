from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentHandler:

    def __init__(self):
          self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        

    def read_document(file_path):
            # TODO implementieren der Pipeline für das extrhieren des Textes aus den Daten 
            return None 
    

    #nützliche Funktionen:
    #text_splitter.split_text(content) -> gibt die Chunks zurück
    #text_splitter.create_documents(chunks, [{"source": source}] * len(chunks
    #text_splitter.from_tiktoken_encoder()


    #eigene funktion für das erstellen von Dokumenten aus den Chunks
    # def create_documents_from_chunks(chunks, source):
    # documents = []
    # for chunk in chunks:
    #     documents.append(
    #         Document(
    #             page_content=chunk,
    #             metadata={"source": source}
    #         )
    #     )        
    # return documents