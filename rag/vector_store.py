from pathlib import Path

class ChromaVectorStore:
    def __init__(self, persist_directory="./chroma_db",
                 collection_name="utility_reconciliation"):
        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError(
                "ChromaDB is not installed. Run: pip install chromadb"
            ) from exc

        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Utility and telecom reconciliation knowledge"},
        )

    def upsert_documents(self, documents):
        if not documents:
            return 0
        ids, texts, metadatas = [], [], []
        for i, doc in enumerate(documents):
            ids.append(f"{doc.source}:{i}")
            texts.append(doc.text)
            metadatas.append(doc.metadata)
        self.collection.upsert(ids=ids, documents=texts, metadatas=metadatas)
        return len(documents)

    def query(self, query_text, n_results=4):
        if self.collection.count() == 0:
            return []
        result = self.collection.query(
            query_texts=[query_text],
            n_results=min(n_results, self.collection.count()),
        )
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        return [
            {"text": text, "metadata": metadata, "distance": distance}
            for text, metadata, distance in zip(docs, metas, distances)
        ]
