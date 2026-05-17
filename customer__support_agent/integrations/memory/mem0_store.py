from __future__ import annotations
from typing import Any
from customer__support_agent.core.settings import Settings

try:
    from mem0 import Memory
except:
    Memory = None


class CustomerMemoryStore:
    def __init__(self, settings: Settings,llm:Any):
        pass

    def search(self, query:str,user_id:str,limit:int = 5) -> list[dict[str,Any]]:
        pass

    def list_memories(self, user_id:str, limit:int = 20) -> list[dict[str,Any]]:
        pass

    def add_interaction(
        self,
        user_id:str,
        user_input:str,
        assistant_response:str,
        metadata: dict[str,Any] | None = None,
    ) -> None:
        pass

    def add_resolution(
        self,
        user_id:str,
        ticket_subject:str,
        ticket_description:str,
        accepted_draft:str,
        entity_links: list[str] | None = None,
    ) -> None:
        pass

    def _add_messages(
        self,
        messages: list[dict[str,str]],
        user_id:str,
        metadata: dict[str,Any] | None = None,
    ) -> None:
        pass

    def _normalize_results(self,raw:Any, limit:int)-> list[dict[str,Any]]:
        pass
