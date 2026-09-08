from sentence_transformers import SentenceTransformer
import faiss
import json
from pathlib import Path


VECTOR_DIR = Path("vector_store")
VECTOR_DIR.mkdir(exist_ok=True)

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

SIMILARITY_THRESHOLD = 0.30


class RAGService:

    def __init__(self):
        self.embedding_model = SentenceTransformer(
            "BAAI/bge-small-en-v1.5"
        )

    def chunk_text(
            self,
            text: str,
            chunk_size: int = CHUNK_SIZE,
            overlap: int = CHUNK_OVERLAP,
    ):
        text = text.strip()

        if not text:
            return []

        chunks = []

        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start += chunk_size - overlap

        return chunks

    def chunk_documents(
            self,
            documents: list[dict],
    ):
        chunks = []

        for document in documents:
            source = document["source"]
            source_type = document["type"]
            text = document["text"]

            text_chunks = self.chunk_text(text)

            for chunk in text_chunks:
                chunks.append({
                    "text": chunk,
                    "source": source,
                    "type": source_type,
                })

        return chunks

    def create_embeddings(
            self,
            chunks: list[dict],
    ):
        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        return self.embedding_model.encode(
            texts,
            normalize_embeddings=True,
        )

    def save_document(
            self,
            document_id: str,
            chunks: list[dict],
    ):
        if not chunks:
            raise ValueError(
                "No document content found."
            )

        embeddings = self.create_embeddings(
            chunks
        )

        dimension = embeddings.shape[1]

        index = faiss.IndexFlatIP(
            dimension
        )

        index.add(embeddings)

        index_path = (
                VECTOR_DIR /
                f"{document_id}.index"
        )

        metadata_path = (
                VECTOR_DIR /
                f"{document_id}.json"
        )

        faiss.write_index(
            index,
            str(index_path),
        )

        metadata = {
            "document_id": document_id,
            "chunks": chunks,
        }

        metadata_path.write_text(
            json.dumps(
                metadata,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return {
            "document_id": document_id,
            "chunk_count": len(chunks),
            "embedding_dimension": dimension,
        }

    def search(
            self,
            document_id: str,
            query: str,
            top_k: int = 5,
    ):
        index_path = (
                VECTOR_DIR /
                f"{document_id}.index"
        )

        metadata_path = (
                VECTOR_DIR /
                f"{document_id}.json"
        )

        if not index_path.exists():
            raise ValueError(
                f"Document not found: {document_id}"
            )

        index = faiss.read_index(
            str(index_path)
        )

        metadata = json.loads(
            metadata_path.read_text(
                encoding="utf-8"
            )
        )

        query_embedding = (
            self.embedding_model.encode(
                [query],
                normalize_embeddings=True,
            )
        )

        search_count = min(
            max(top_k * 2, top_k),
            index.ntotal,
        )

        scores, indices = index.search(
            query_embedding,
            search_count,
        )

        results = []

        for score, index_id in zip(
                scores[0],
                indices[0],
        ):
            if index_id < 0:
                continue

            score = float(score)

            if score < SIMILARITY_THRESHOLD:
                continue

            chunk = metadata["chunks"][index_id]

            results.append({
                "text": chunk["text"],
                "source": chunk["source"],
                "type": chunk["type"],
                "score": score,
            })

            if len(results) >= top_k:
                break

        return results