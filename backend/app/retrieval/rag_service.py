"""
Retrieval-Augmented Generation (RAG) Service
Coordinates Hybrid Retrieval, Context Assembly, and OpenRouter Gemini Inference
to produce grounded, hallucination-free operational intelligence and recommendations.
"""
from typing import Any, Dict, List, Optional
from backend.app.core.llm_client import OpenRouterLLMClient, get_llm_client
from backend.app.retrieval.hybrid_search import HybridRetriever, get_hybrid_retriever

class RAGService:
    def __init__(
        self,
        retriever: Optional[HybridRetriever] = None,
        llm_client: Optional[OpenRouterLLMClient] = None
    ):
        self.retriever = retriever or get_hybrid_retriever()
        self.llm_client = llm_client or get_llm_client()

    def build_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """Format retrieved reviews into structured context with source citations."""
        if not retrieved_docs:
            return "No relevant historical reviews found in the database."

        context_lines = []
        for i, doc in enumerate(retrieved_docs, 1):
            meta = doc.get("metadata", {})
            restaurant = meta.get("restaurant", "Unknown Restaurant")
            category = meta.get("category", "General")
            aspect = meta.get("complaint_type", "general")
            rating = meta.get("rating", "N/A")
            priority = meta.get("priority_score", "N/A")
            date = meta.get("date", "Unknown Date")
            doc_id = doc.get("id", f"REV_{i}")
            text = doc.get("text", "").strip()

            context_lines.append(
                f"[Source #{i} | ID: {doc_id}]\n"
                f"Restaurant: {restaurant} | Rating: {rating} Stars | Date: {date}\n"
                f"Category: {category} | Aspect: {aspect} | Priority Score: {priority}\n"
                f"Review Text: \"{text}\"\n"
            )

        return "\n----------------------------------------\n".join(context_lines)

    def answer_query(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute full end-to-end RAG pipeline:
        1. Hybrid Search
        2. Context Assembly
        3. Grounded Gemini LLM Inference
        4. Structured Output Formatting
        """
        # 1. Retrieve hybrid search candidates
        retrieved_docs = self.retriever.search(
            query=query,
            k=k,
            filter_dict=filter_dict
        )

        # 2. Assemble context
        context_str = self.build_context(retrieved_docs)

        # 3. Create Grounded Prompt
        system_prompt = (
            "You are an expert Restaurant Operations AI Consultant. Your mission is to analyze restaurant manager "
            "queries and provide rigorous, grounded operational answers based strictly on the retrieved Yelp reviews.\n\n"
            "STRICT RULES:\n"
            "1. Rely ONLY on the facts directly stated in the provided Context.\n"
            "2. DO NOT hallucinate or assume unmentioned details.\n"
            "3. Cite source IDs (e.g. [Source #1], [Source #2]) when mentioning specific incidents or data points.\n"
            "4. Structure your response into:\n"
            "   - Executive Diagnosis & Problem Classification\n"
            "   - Root-Cause Evidence Breakdown\n"
            "   - Actionable Managerial Recommendations (Immediate & Long-Term)\n"
            "   - Risk & Business Impact Analysis"
        )

        user_prompt = (
            f"Manager Question: \"{query}\"\n\n"
            f"=== RETRIEVED HISTORICAL REVIEWS CONTEXT ===\n"
            f"{context_str}\n\n"
            "Please provide your grounded operational diagnosis and actionable recommendations based on the evidence above."
        )

        # 4. LLM Generation
        answer_text = self.llm_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            model=model
        )

        # 5. Extract Citations
        citations = []
        for i, doc in enumerate(retrieved_docs, 1):
            meta = doc.get("metadata", {})
            citations.append({
                "source_index": i,
                "review_id": doc.get("id"),
                "restaurant": meta.get("restaurant"),
                "category": meta.get("category"),
                "aspect": meta.get("complaint_type"),
                "rating": meta.get("rating"),
                "priority_score": meta.get("priority_score"),
                "rrf_score": doc.get("rrf_score")
            })

        return {
            "query": query,
            "answer": answer_text,
            "retrieved_reviews": retrieved_docs,
            "citations": citations,
            "evidence_count": len(retrieved_docs),
            "model_used": model or self.llm_client.default_model
        }

# Global singleton
_rag_instance: Optional[RAGService] = None

def get_rag_service() -> RAGService:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGService()
    return _rag_instance
