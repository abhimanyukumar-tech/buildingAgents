from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

@dataclass
class Document:
    text: str
    source: str
    metadata: Dict[str, str]

def load_text_documents(root: str = "data") -> List[Document]:
    documents = []
    root_path = Path(root)
    for path in sorted(root_path.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}:
            text = path.read_text(encoding="utf-8").strip()
            if text:
                documents.append(Document(
                    text=text,
                    source=str(path),
                    metadata={
                        "source": str(path),
                        "category": path.parent.name,
                        "filename": path.name,
                    },
                ))
    return documents
