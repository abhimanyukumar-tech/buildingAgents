from dotenv import load_dotenv

from rag.documents import load_text_documents
from rag.vector_store import ChromaVectorStore
from rag.retriever import ReconciliationRetriever
from rag.reasoning import AzureFoundryReasoner

def build_knowledge_base():
    load_dotenv()
    documents = load_text_documents("data")
    store = ChromaVectorStore(
        persist_directory="./chroma_db",
        collection_name="utility_reconciliation",
    )
    count = store.upsert_documents(documents)
    print(f"Loaded {count} documents into ChromaDB.")
    return store

def retrieve_evidence(query, top_k=4):
    store = build_knowledge_base()
    matches = ReconciliationRetriever(store).retrieve(query, top_k)
    print(ReconciliationRetriever.build_context(matches))
    return matches

def classify_dispute(dispute_text, top_k=4):
    load_dotenv()
    store = build_knowledge_base()
    retriever = ReconciliationRetriever(store)
    matches = retriever.retrieve(dispute_text, top_k)
    result = AzureFoundryReasoner().classify(dispute_text, matches)
    print(result)
    return result

if __name__ == "__main__":
    print("Stage 2 RAG module ready.")
