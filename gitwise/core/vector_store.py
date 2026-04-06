from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance, PointsSelector
import logging
import time


class VectorStore:

    def __init__(self, client, collection_name: str = "gitwise_code", vector_dim: int = 384):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.client = client
        self.collection_name = collection_name
        self.vector_dim = vector_dim
        self.create_collection()

    def create_collection(self, distance=Distance.COSINE):
        try:
            collections = [c.name for c in self.client.get_collections().collections]
            if self.collection_name not in collections:
                self.logger.info(f"Creating collection '{self.collection_name}'...")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.vector_dim, distance=distance)
                )
            else:
                self.logger.info(f"Collection '{self.collection_name}' already exists")
        except Exception as e:
            self.logger.warning(f"Collection creation skipped: {e}")

    def insert_update_vector(self, ids, embeddings, payloads, batch_size=100, delay=0.1):
        """
        Insert or update vectors in Qdrant using batching.

        Args:
            ids (List[str])
            embeddings (List[List[float]])
            payloads (List[dict])
        """

        if len(embeddings[0]) != self.vector_dim:
            raise ValueError(
                f"Embedding dimension {len(embeddings[0])} "
                f"does not match collection dim {self.vector_dim}"
            )

        total = len(ids)

        for i in range(0, total, batch_size):
        # Insert vectors in batches to avoid large HTTP requests that may cause
        # connection resets, timeouts, or memory/buffer limits in Qdrant.
            batch_ids = ids[i:i+batch_size]
            batch_vectors = embeddings[i:i+batch_size]
            batch_payloads = payloads[i:i+batch_size]

            points = [
                PointStruct(
                    id=batch_ids[j],
                    vector=batch_vectors[j],
                    payload=batch_payloads[j],
                )
                for j in range(len(batch_ids))
            ]

            result = self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            self.logger.info(
                f"Upserted batch {i}-{i+len(points)} "
                f"({len(points)} vectors). Result: {result}"
            )

            time.sleep(delay)

    def search_vectors(self, query_vector, limit=5):

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            with_payload=True
        )

        self.logger.info(
            f"Searched {self.collection_name} with query vector "
            f"(dim={len(query_vector)}). Top {limit} results returned."
        )

        return results.points

    def delete_vectors(self, ids):

        self.client.delete(
            collection_name=self.collection_name,
            points_selector=PointsSelector(ids=ids)
        )

        self.logger.info(
            f"Deleted vectors with IDs: {ids} from {self.collection_name}"
        )

    def delete_collection(self, collection_name):

        if self.client.collection_exists(collection_name):

            self.logger.info(f"Deleting collection '{collection_name}'...")

            self.client.delete_collection(collection_name)