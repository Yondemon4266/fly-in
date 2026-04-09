from pydantic import (
    BaseModel,
    Field,
)
from src.models.hub import Hub
from src.models.connection import Connection


class MapConfig(BaseModel):
    """Top-level validated configuration for a parsed map.

    Attributes:
        nb_drones: Number of drones to simulate.
        start_hub: Start hub for all drones.
        end_hub: Destination hub for all drones.
        hubs: Parsed hubs defined in the map.
        connections: Parsed connections between hubs.
    """

    nb_drones: int = Field(default=1, gt=0)
    start_hub: Hub = Field(...)
    end_hub: Hub = Field(...)
    hubs: list[Hub] = Field(default_factory=list)
    connections: list[Connection] = Field(min_length=1)
