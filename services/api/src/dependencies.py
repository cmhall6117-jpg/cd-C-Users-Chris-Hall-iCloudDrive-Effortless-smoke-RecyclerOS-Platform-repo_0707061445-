from fastapi import Request

from store import WorkflowStore


def get_store(request: Request) -> WorkflowStore:
    return request.app.state.store
