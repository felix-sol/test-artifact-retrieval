import unittest
from pathlib import Path
from qdrant_client.models import PointStruct
from EmbeddingService import EmbeddingService
from data_ingestion.TextProcessor import TextProcessor
from knowledge_base.DatabaseManager import DatabaseManager

# tests run on a small selection of data from the original pipeline 
class TestDocumentHandlerPipeline(unittest.TestCase):

  def setUp(self):
    self.textProcessor = TextProcessor()
    self.embeddingService = EmbeddingService()
    self.databaseManager = DatabaseManager()
    self.input_root = Path("/home/WERUM/felix_soltau/projects/private/git/test-artifact-retrieval/data_ingestion/test/resources/test_data")  
    self.small_documents_root = Path("/home/WERUM/felix_soltau/projects/private/git/test-artifact-retrieval/data_ingestion/test/resources/test_data/small_test_data")


  # compare the plain amount of files in the input dir with assesed files of reading step
  def test_number_of_files_processed(self):
    amount_of_files_in_input_dir = sum(1 for file in self.input_root.iterdir() if file.is_file())
    amount_of_files_read = 0

    for file in self.input_root.iterdir():
      if not file.is_file():
        continue

      with open(file, "r", encoding="utf-8") as f:
                content, metadata = self.textProcessor.read_file_and_return_text(f)

      self.assertTrue(metadata, f"Metadata for file {file} should not be empty.")
      self.assertTrue(content.strip(), f"Content for file {file} should not be empty.")
      amount_of_files_read += 1

    self.assertEqual(amount_of_files_in_input_dir, amount_of_files_read, "Number of files read does not match number of files in input directory.")


  # test that the number of documents created from the files matches the number of chunks created from the content of each file
  def test_number_of_files_matching_documents_created(self):
    amount_of_files_in_input_dir = sum(1 for file in self.input_root.iterdir() if file.is_file())
    processed_files = set()
    
    for file in self.input_root.iterdir():
      if not file.is_file():
        continue

      with open(file, "r", encoding="utf-8") as f:
                content, metadata = self.textProcessor.read_file_and_return_text(f)

      text_chunks = self.textProcessor.chunk_text_from_file(content)
      documents_from_single_file = self.textProcessor.create_documents_from_chunks(text_chunks, metadata)

      self.assertGreaterEqual(len(documents_from_single_file), 1, f"{file} produced no documents.")
      self.assertEqual(len(documents_from_single_file), len(text_chunks), f"Number of documents created from {file} does not match number of chunks.")

      # each file which goes through processing should have its metadata and then attached to the each document created
      processed_files.add(documents_from_single_file[0].metadata["filename"])

    # shows that each file in input dir has been processed and created at 
    self.assertEqual(amount_of_files_in_input_dir, len(processed_files), "Number of processed files does not match number of files in input directory.")
    

  #test if the returned embedding list matches each item of the list handed to the EmbeddingService and that the embedding is not empty
  def test_correct_mapping_of_embeddings_to_documents(self):
      documents_to_embed, contents, embeddings, points = self.build_documents_embeddings_points()
      self.assertEqual([doc.page_content for doc in documents_to_embed], contents)
      self.assertEqual(len(embeddings), len(contents), "Number of embeddings does not match number of contents.")
      
      for embedding in embeddings:
          self.assertIsInstance(embedding, list, "Embedding is not a list.")
          self.assertGreater(len(embedding), 0, "Embedding is empty.")

      points = [
            PointStruct(
                id=index,
                vector=embedding,
                payload={
                    "content": document.page_content,
                    **document.metadata,
                },
            )
            for index, (document, embedding) in enumerate(zip(documents_to_embed, embeddings, strict=True))
        ]    
      
      for i, point in enumerate(points):
          self.assertEqual(point.id, i)
          self.assertEqual(point.payload["content"], documents_to_embed[i].page_content)
          self.assertEqual(point.vector, embeddings[i])


  # run the docker compose file to be able to access the database first
  # tests if the data is stored correctly
  def test_storage_in_vector_database(self):
      documents_to_embed, contents, embeddings, points = self.build_documents_embeddings_points()

      collection_name = "test_collection"
      if self.databaseManager.client.collection_exists(collection_name=collection_name):
        self.databaseManager.client.delete_collection(collection_name=collection_name)  # clean up before test
      
      self.databaseManager.create_collection(
          collection_name=collection_name, 
          vector_size=len(embeddings[0])
          )
      
      self.databaseManager.upsert_points(
          collection_name=collection_name,
          points=points
      )

      collection_info = self.databaseManager.client.get_collection(collection_name=collection_name) 
      self.assertIsNotNone(collection_info, "Collection 'test_collection' was not created successfully.")

      count = self.databaseManager.client.count(collection_name=collection_name).count
      self.assertEqual(count, len(points), "Number of points stored in the vector database")

      stored_points = self.databaseManager.client.retrieve(
          collection_name=collection_name,
          ids=[point.id for point in points]
      )
      self.assertEqual(len(stored_points), len(points), "Not all points were retrieved.")

      for original, stored in zip(points, stored_points):
          self.assertEqual(stored.id, original.id)
          self.assertEqual(stored.payload["content"] , original.payload["content"])
          for key, value in original.payload.items():
              self.assertEqual(stored.payload[key], value)
      
      
  # helper method to build documents, embeddings and points for testing    
  def build_documents_embeddings_points(self):
      documents_to_embed = self.textProcessor.process_documents(self.input_root)
      contents = [doc.page_content for doc in documents_to_embed]
      embeddings = self.embeddingService.generate_embeddings_for_documents(contents)
      points = [
            PointStruct(
                id=index,
                vector=embedding,
                payload={
                    "content": document.page_content,
                    **document.metadata,
                },
            )
            for index, (document, embedding) in enumerate(zip(documents_to_embed, embeddings, strict=True))
        ]
      return documents_to_embed, contents, embeddings, points

  
if __name__ == "__main__":
    unittest.main()
