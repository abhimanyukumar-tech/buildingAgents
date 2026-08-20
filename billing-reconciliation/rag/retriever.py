class ReconciliationRetriever:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def retrieve(self, query, top_k=4):
        return self.vector_store.query(query, n_results=top_k)

    @staticmethod
    def build_context(matches):
        if not matches:
            return "No supporting documents were retrieved."
        return "\n\n".join(
            f"[Source {i}: {m['metadata'].get('source', 'unknown')}]\n{m['text']}"
            for i, m in enumerate(matches, start=1)
        )
