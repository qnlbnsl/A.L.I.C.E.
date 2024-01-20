import os
from typing import Self

from pydantic import BaseModel

class ApiRoutes(BaseModel):
    invitation: str = "/invitation"

class ArguFlowManager:
    def __init__(self: Self, host: str) -> None:
        self.host = host
        self._authorization = os.getenv("ARGUFLOW_AUTHORIZATION")
        self._headers = { "Content-Type": "application/json", "Authorization": self._authorization}
        self.api_base_url = f"{self.host}/api/"
    
        