from __future__ import annotations
from customer__support_agent.core.settings import Settings
from customer__support_agent.integrations.rag.chroma_kb import KnowledgeBaseService

class KnowledgeService:
    def __init__(self, settings:Settings):
        self._settings = settings

    def ingest(self, clear_existing:bool = False) -> dict[str,Any]:
        rag_servie = KnowledgeBaseService(settings=self._settings)
        return rag_servie.ingest_directory(
            directory=self._settings.knowledge_base_path,
            clear_existing=clear_existing
        )
