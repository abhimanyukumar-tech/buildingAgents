import json
import os

SYSTEM_PROMPT = """You are a utility and telecom billing reconciliation assistant.

Use only the supplied retrieved evidence for factual claims about disputes,
outages, credits, policies, or adjustment reasons.

Return a concise JSON object with:
- adjustment_code
- adjustment_category
- rationale
- evidence_sources
- confidence

If evidence is insufficient or contradictory, set adjustment_code to null
and confidence below 0.70.
"""

class AzureFoundryReasoner:
    def __init__(self, endpoint=None, api_key=None, api_version=None, deployment=None):
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
        self.deployment = deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT")

    def _validate_config(self):
        missing = []
        if not self.endpoint:
            missing.append("AZURE_OPENAI_ENDPOINT")
        if not self.api_key:
            missing.append("AZURE_OPENAI_API_KEY")
        if not self.deployment:
            missing.append("AZURE_OPENAI_DEPLOYMENT")
        if missing:
            raise RuntimeError("Azure reasoning is not configured. Missing: " + ", ".join(missing))

    def classify(self, dispute_text, retrieved_matches):
        self._validate_config()
        try:
            from openai import AzureOpenAI
        except ImportError as exc:
            raise RuntimeError("OpenAI SDK is not installed. Run: pip install openai") from exc

        context = "\\n\\n".join(
            f"Source {i}: {m['metadata'].get('source', 'unknown')}\\n{m['text']}"
            for i, m in enumerate(retrieved_matches, start=1)
        ) or "No evidence."

        client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint,
        )
        response = client.chat.completions.create(
            model=self.deployment,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": (
                    "Classify this dispute using only the evidence below.\\n\\n"
                    f"Dispute:\\n{dispute_text}\\n\\n"
                    f"Retrieved evidence:\\n{context}"
                )},
            ],
        )
        return json.loads(response.choices[0].message.content)
