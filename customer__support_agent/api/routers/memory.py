""" Customer memory routes."""

from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException

from customer__support_agent.api.dependencies import (
    get_copilot_or_503,
    get_customers_repository
)
from customer__support_agent.repositories.sqlite.customer import CustomersRepository
from customer__support_agent.schemas.api import CustomerMemoriesResponse, CustomerMemorySearchResponse
from customer__support_agent.services.copilot_service import SupportCopilot

router = APIRouter()

@router.get("/api/memories/{customer_id}/memories", response_model=CustomerMemoriesResponse)
def customer_memories_route(
    customer_id:int,
    customers_repo:CustomersRepository = Depends(get_customers_repository),
    copilot:SupportCopilot = Depends(get_copilot_or_503),
) -> dict:
    customer = customers_repo.get_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    try:
        memories = copilot.get_memories(
            customer_email=customer["email"],
            customer_company=customer.get("company"),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to get memories: {exc}") from exc

    return {
        "customer_id": customer_id,
        "customer_email": customer["email"],
        "memories": memories,
    }


@router.get("/api/customers/{customer_id}/memory-search", response_model=CustomerMemorySearchResponse):
def customer_memory_search_route(
    customer_id:int,
    query:str,
    limit:int = 10,
    customers_repo:CustomersRepository = Depends(get_customers_repository),
    copilot:SupportCopilot = Depends(get_copilot_or_503),
) -> dict:
    customer= customers_repo.get_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query is required")

    try:
        results = copilot.search_customer_memories(
            customer_email=customer["email"],
            customer_company=customer.get("company"),
            query=query,
            limit=max(1,min(limit,25)),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to search memories: {exc}") from exc

    return {
        "customer_id": customer_id,
        "customer_email": customer["email"],
        "query": query,
        "results": results
    }
