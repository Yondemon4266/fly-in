from pydantic import (
    BaseModel,
    Field,
)
from src.models.hub import Hub
from src.models.connection import Connection


class MapConfig(BaseModel):
    nb_drones: int = Field(default=1, gt=0)
    start_hub: Hub = Field(...)
    end_hub: Hub = Field(...)
    hubs: list[Hub] = Field(default_factory=list)
    connections: list[Connection] = Field(min_length=1)
