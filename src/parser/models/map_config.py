from pydantic import (
    BaseModel,
    Field,
)
from src.parser.models.hub import Hub
from src.parser.models.connection import Connection


class MapConfig(BaseModel):
    nb_drones: int
    start_hub: Hub = Field(...)
    end_hub: Hub = Field(...)
    hubs: list[Hub] = Field(default_factory=list)
    connections: list[Connection] = Field(min_length=1)
