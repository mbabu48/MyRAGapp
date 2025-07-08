from vector_store import VectorStore
from llm_client import LLMClient
from typing import List, Dict, Any
from config import load_config

class CoreRAG:
    def __init__(self, config):
        self.llm = LLMClient(config)
        self.vector_store = VectorStore(config)
        self.embedding_model = config.get('EMBEDDING_MODEL', 'text-embedding-3-small')
        self.chat_model = config.get('CHAT_MODEL', 'gpt-4o-mini')

    def add_documents(self, documents: List[Dict[str, Any]]):
        self.vector_store.add_documents(documents, self.llm, self.embedding_model)

    def search_documents(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        return self.vector_store.search(query, n_results, self.llm, self.embedding_model)

    def generate_response(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        context = "\n\n".join([doc['text'] for doc in context_docs])
        prompt = f"""Based on the following context, please answer the question.\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:"""
        return self.llm.chat(prompt, self.chat_model)

    def query(self, question: str, n_results: int = 3) -> Dict[str, Any]:
        relevant_docs = self.search_documents(question, n_results)
        response = self.generate_response(question, relevant_docs)
        return {
            'question': question,
            'answer': response,
            'sources': relevant_docs
        }

    def get_collection_info(self) -> Dict[str, Any]:
        return self.vector_store.get_info()


def main():
    """
    Main function to execute the CoreRAG workflow.
    """
    config = load_config()
    core_rag = CoreRAG(config)

    # Example documents to add
    documents = [
        {'text': 'This is a sample document.', 'metadata': {'source': 'example1.md'}},
        {'text': 'This is another sample document.', 'metadata': {'source': 'example2.md'}}
    ]

    # Add documents to the vector store
    core_rag.add_documents(documents)

    # Query the vector store
    question = "What is a sample document?"
    response = core_rag.query(question)
    
    print("Response:", response)

if __name__ == "__main__":
    main()