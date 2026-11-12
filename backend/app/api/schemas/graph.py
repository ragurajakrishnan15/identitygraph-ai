from pydantic import BaseModel


class NetworkResponse(BaseModel):
    nodes: list[dict]
    edges: list[dict]
    summary: dict
    note: str
