# Automated Utility & Telecom Billing Reconciliation System
An Agentic AI Workflow using LangGraph, the Microsoft Agent Framework, and the Model Context Protocol (MCP) that automates this entire matching and reconciliation process without human intervention.

## Stage 1
Run:

```bash
python -m pip install -r requirements.txt
python main.py
python tests.py
```

## Stage 2 — RAG + ChromaDB + Azure AI Foundry

Copy `.env.example` to `.env` and fill in:

```env
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_API_VERSION=2024-10-21
AZURE_OPENAI_DEPLOYMENT=
```

Add knowledge documents under:

```text
data/disputes/
data/outages/
```

Build the ChromaDB knowledge base:

```bash
python -c "from stage2_rag import build_knowledge_base; build_knowledge_base()"
```

Test retrieval:

```bash
python -c "from stage2_rag import retrieve_evidence; retrieve_evidence('meter reading estimated too high')"
```

When Azure is configured, test grounded classification:

```bash
python -c "from stage2_rag import classify_dispute; classify_dispute('The meter reading was estimated too high and should be corrected.')"
```

Do not commit `.env` or API keys to Git.
