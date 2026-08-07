from pydantic import BaseModel


# This is the documented response model for the health endpoint.
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str
