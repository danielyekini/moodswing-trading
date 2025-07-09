from pydantic import BaseModel
from typing import Optional

class ProblemDetails(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: Optional[str] = None
    trace_id: Optional[str] = None 