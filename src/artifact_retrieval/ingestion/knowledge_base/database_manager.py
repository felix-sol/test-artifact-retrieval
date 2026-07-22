from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, PointStruct
from artifact_retrieval.ingestion.knowledge_base.config.knowledge_base_config import DISTANCE, QDRANT_URL
import logging

class DatabaseManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = QdrantClient(url=QDRANT_URL)


    def create_collection(self, collection_name: str, vector_size: int):
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=DISTANCE),
        )
        self.logger.info(f"Collection '{collection_name}' created with vector size {vector_size} and distance {DISTANCE}.")
        
    def upsert_points(self, collection_name: str, points: list[PointStruct]):
        operation_info = self.client.upsert(
            collection_name=collection_name,
            wait=True,
            points=points,
        )
        self.logger.info(f"Upsert operation info: {operation_info}")
        return operation_info    
    

    def upsert_points_in_batches(self, collection_name: str, points: list[PointStruct]):
        points_batches = self.prepare_batches(points)
        for batch in points_batches:
            self.upsert_points(collection_name, batch)

    # split upsert operation into smaller batches
    def prepare_batches(self, points: list[PointStruct]) -> list[list[PointStruct]]:
        points_batches = []
        current_batch = []
        batch_size = 50

        for point in points:
            current_batch.append(point)
            if len(current_batch) >= batch_size:
                points_batches.append(current_batch)
                current_batch = []

        if current_batch:
            points_batches.append(current_batch)        

        return points_batches    