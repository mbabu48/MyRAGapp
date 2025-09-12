import chromadb
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class VectorStore:
    def __init__(self, config):
        self.collection_name = "rag_documents"
        self.chroma_client = chromadb.PersistentClient(path=config.get('CHROMA_DB_PATH', './chroma_db'))
        try:
            self.collection = self.chroma_client.get_collection(name=self.collection_name)
        except:
            self.collection = self.chroma_client.create_collection(name=self.collection_name)
        self.tfidf_vectorizer = TfidfVectorizer()
        self.sparse_matrix = None
        self.texts = []

    def add_documents(self, documents: List[Dict[str, Any]], llm, embedding_model):
        texts, embeddings, metadatas, ids = [], [], [], []
        for i, doc in enumerate(documents):
            text = doc['text']
            metadata = doc.get('metadata', {})
            doc_id = doc.get('id', f"doc_{i}")
            embedding = llm.create_embedding(text, embedding_model)
            texts.append(text)
            embeddings.append(embedding)
            metadatas.append(metadata)
            ids.append(doc_id)
        # Fit TF-IDF vectorizer on all texts
        self.texts.extend(texts)
        self.sparse_matrix = self.tfidf_vectorizer.fit_transform(self.texts)
        # Store both dense and sparse vectors in ChromaDB
        self.collection.add(documents=texts, embeddings=embeddings, metadatas=metadatas, ids=ids)

    def search(self, query: str, n_results: int, llm, embedding_model, hybrid_weight: float = 0.5) -> List[Dict[str, Any]]:
        # Dense embedding for query
        query_embedding = llm.create_embedding(query, embedding_model)
        # Sparse vector for query
        query_sparse = self.tfidf_vectorizer.transform([query])
        # ChromaDB hybrid search (if supported)
        # If ChromaDB hybrid search API is available, use it. Otherwise, combine results manually.
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                query_sparse_vectors=[query_sparse.toarray()[0]],
                n_results=n_results,
                # ChromaDB hybrid search API may accept a weight parameter
                hybrid_search_weight=hybrid_weight
            )
        except Exception as e:
            # Fallback: combine dense and sparse scores manually
            dense_results = self.collection.query(query_embeddings=[query_embedding], n_results=n_results)
            # Compute sparse similarities
            sparse_scores = np.dot(self.sparse_matrix, query_sparse.T).toarray().flatten()
            # Combine scores
            combined_scores = []
            for i, doc in enumerate(self.texts):
                dense_score = 1.0
                if doc in dense_results['documents'][0]:
                    idx = dense_results['documents'][0].index(doc)
                    dense_score = dense_results['distances'][0][idx]
                sparse_score = sparse_scores[i]
                score = hybrid_weight * dense_score + (1 - hybrid_weight) * sparse_score
                combined_scores.append((score, i))
            # Get top n_results
            top_indices = sorted(combined_scores, key=lambda x: x[0], reverse=True)[:n_results]
            search_results = []
            for score, idx in top_indices:
                search_results.append({
                    'text': self.texts[idx],
                    'metadata': {},
                    'distance': score,
                    'id': f"doc_{idx}"
                })
            return search_results
        # Standard result parsing
        search_results = []
        for i in range(len(results['documents'][0])):
            search_results.append({
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i],
                'id': results['ids'][0][i]
            })
        return search_results

    def get_info(self) -> Dict[str, Any]:
        return {
            'collection_name': self.collection_name,
            'document_count': self.collection.count()
        }

    def clear(self):
        self.chroma_client.delete_collection(name=self.collection_name)
        self.collection = self.chroma_client.create_collection(name=self.collection_name)
        self.texts = []
        self.sparse_matrix = None

