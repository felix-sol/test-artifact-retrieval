import unittest
from pathlib import Path
from data_ingestion.TextProcessor import TextProcessor

# tests run on a small selection of data from the original pipeline 
class TestTextProcessor(unittest.TestCase):

  def setUp(self):
    self.textProcessor = TextProcessor()
    self.input_root = Path("/home/WERUM/felix_soltau/projects/private/git/test-artifact-retrieval/data_ingestion/test/resources/test_data")  
    self.small_documents_root = Path("/home/WERUM/felix_soltau/projects/private/git/test-artifact-retrieval/data_ingestion/test/resources/test_data/small_test_data")


  # assure that each document has set metadata and page_content attributes
  def test_documents_have_metadata_and_page_content(self):
    for file in self.input_root.iterdir():
      if not file.is_file():
        continue

      with open(file, "r", encoding="utf-8") as f:
        content, metadata = self.textProcessor.read_file_and_return_text(f)

      text_chunks = self.textProcessor.chunk_text_from_file(content)
      documents_from_single_file = self.textProcessor.create_documents_from_chunks(text_chunks, metadata)

      for doc in documents_from_single_file:
        self.assertIsInstance(doc.metadata, dict, f"Document from file {file} has no metadata dictionary.")
        self.assertTrue(doc.metadata, f"Document from file {file} has an empty metadata dictionary.")
        self.assertTrue(doc.page_content.strip(), f"Document from file {file} has empty page_content.")
      

  # test that the metadata extracted from the files is correct and matches the expected keys
  def test_extraction_of_metadata(self):
    allowed_metadata_keys = {"filename", "repo_name", "rel_path", "source_type"}

    for file in self.input_root.iterdir():
      if not file.is_file():
        continue

      with open(file, "r", encoding="utf-8") as f:
        content, metadata = self.textProcessor.read_file_and_return_text(f)

      self.assertTrue(metadata, f"Metadata for file {file} should not be empty.")
      
      # story files have an additional metadata key as "file_meta" from "Meta:" annotation in file
      expected_keys = allowed_metadata_keys | {"file_meta"} if file.suffix == ".story" else allowed_metadata_keys 
      
      self.assertEqual(set(metadata.keys()), expected_keys, f"Metadata keys for file {file} do not match expected keys.")
      
      for key in allowed_metadata_keys:
        self.assertTrue(metadata[key], f"Metadata value for key '{key}' in file {file} should not be empty.")


  # test if the page content has the filtered keywords, explicitly scenario or Given When Then
  def test_if_chunks_contain_expected_keywords(self):
    for file in self.input_root.iterdir():
      if not file.is_file():
        continue

      with open(file, "r", encoding="utf-8") as f:
        content, metadata = self.textProcessor.read_file_and_return_text(f)

      text_chunks = self.textProcessor.chunk_text_from_file(content)
      documents_from_single_file = self.textProcessor.create_documents_from_chunks(text_chunks, metadata) 
  
      for document in documents_from_single_file:
        self.assertTrue(document.page_content.strip(), f"Document from file {file} has empty page_content.")
        self.assertIn("Scenario:", document.page_content, f"Document from file {file} does not contain 'Scenario:' in page_content.")      
        # Even if a file has no Scenario in itself, it has a blank annotation which it gets chunked by

  # assure that documents with less than 256 tokens are not chunked
  def test_if_documents_smaller_than_256_tokens_are_single_chunk(self):
    all_chunks = []
    for file in self.small_documents_root.iterdir():
      if not file.is_file():
        continue

      with open(file, "r", encoding="utf-8") as f:
        content, metadata = self.textProcessor.read_file_and_return_text(f)

      text_chunks = self.textProcessor.chunk_text_from_file(content)
      all_chunks.extend(text_chunks)
      self.assertEqual(len(text_chunks), 1, f"File {file} should result in a single chunk, but got {len(text_chunks)} chunks.")


if __name__ == "__main__":
    unittest.main()

