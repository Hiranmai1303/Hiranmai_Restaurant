"""
Vector Store Management using ChromaDB and sentence-transformers/all-MiniLM-L6-v2
Provides indexing, persistent storage, and semantic vector similarity search with rich metadata.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from sentence_transformers import SentenceTransformer
from backend.app.core.config import settings

class LocalSentenceTransformerEmbeddings(EmbeddingFunction[Documents]):
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self._model_name = model_name
        self.model = SentenceTransformer(model_name)

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = self.model.encode(input, convert_to_numpy=True, normalize_embeddings=True)
        return embeddings.tolist()

    def name(self) -> str:
        return "local_sentence_transformers_minilm"

    def get_config(self) -> Dict[str, Any]:
        return {"model_name": self._model_name}

    @classmethod
    def build_from_config(cls, config: Dict[str, Any]) -> "LocalSentenceTransformerEmbeddings":
        return cls(model_name=config.get("model_name", "sentence-transformers/all-MiniLM-L6-v2"))

class ChromaVectorStore:
    def __init__(
        self,
        persist_dir: Optional[str] = None,
        collection_name: str = "restaurant_reviews",
        model_name: Optional[str] = None
    ):
        self.persist_dir = persist_dir or settings.CHROMA_PERSIST_DIR
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        self.embedding_fn = LocalSentenceTransformerEmbeddings(self.model_name)
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ):
        """Add batch of documents with metadata to Chroma collection."""
        self.collection.upsert(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

    def count(self) -> int:
        """Return total number of indexed vectors."""
        try:
            return self.collection.count()
        except Exception:
            try:
                res = self.collection.get()
                return len(res.get("ids", []))
            except Exception:
                return 0

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Perform semantic similarity search with compliant ChromaDB where filtering."""
        where_clause = None
        if filter_dict:
            clean_filters = {
                k_name: v_val
                for k_name, v_val in filter_dict.items()
                if v_val is not None and v_val != "All"
            }
            if len(clean_filters) == 1:
                where_clause = clean_filters
            elif len(clean_filters) > 1:
                where_clause = {"$and": [{k_name: v_val} for k_name, v_val in clean_filters.items()]}

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
        except Exception:
            # Fallback query without where clause to prevent unhandled ChromaDB operator exceptions
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=k,
                    include=["documents", "metadatas", "distances"]
                )
            except Exception:
                results = {}

        formatted = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)
            ids = results["ids"][0] if "ids" in results else [""] * len(docs)

            for doc_id, doc_text, meta, dist in zip(ids, docs, metas, distances):
                score = round(1.0 - float(dist), 4)
                formatted.append({
                    "id": doc_id,
                    "text": doc_text,
                    "metadata": meta,
                    "score": score,
                    "distance": round(float(dist), 4)
                })

        return formatted

# Global singleton
_chroma_instance: Optional[ChromaVectorStore] = None

def get_vector_store() -> ChromaVectorStore:
    global _chroma_instance
    if _chroma_instance is None:
        _chroma_instance = ChromaVectorStore()
    return _chroma_instance
