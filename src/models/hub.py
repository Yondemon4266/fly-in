from pydantic import (
    BaseModel,
    Field,
    model_validator,
    ValidationError,
    ConfigDict,
)
from typing import Any
from src.parser.parser_utils import ParserUtils
from src.models.hub_metadata import HubMetadata
from src.models.connection import Connection


class Hub(BaseModel):
    """Map hub node and its metadata.

    Attributes:
        name: Unique hub identifier.
        x: Horizontal coordinate.
        y: Vertical coordinate.
        metadata: Zone and capacity constraints.
        connections: Outgoing hub connections.
    """

    name: str = Field(...)
    x: int = Field(...)
    y: int = Field(...)
    metadata: HubMetadata
    connections: list[Connection] = Field(default_factory=list)
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def string_to_dict(cls, data: Any) -> Any:
        """Convert a compact hub string into validated model fields.

        Args:
            data: Raw value, usually ``name x y [key=value]``.

        Returns:
            Parsed dictionary for model construction, or original input.

        Raises:
            ValueError: If the hub string is malformed.
        """
        message = (
            "Invalid format for Hub, expected format: "
            "name x y [key=value].\ninput: "
        )
        if isinstance(data, str):
            data_clean = data.strip()
            info_part = data_clean
            meta_dict: dict[str, Any] | str = {}

            if "[" in data_clean:
                parts = data_clean.split("[")
                if len(parts) != 2:
                    raise ValueError(f"{message} {data}")
                info_part = parts[0].strip()
                meta_dict = "[" + parts[1].strip()
            info = info_part.split()
            if len(info) != 3:
                raise ValueError(f"{message} {info_part}")
            try:
                name, x, y = info[0].strip(), int(info[1]), int(info[2])
            except ValueError:
                raise ValueError(f"{message} {data}")

            return {"name": name, "x": x, "y": y, "metadata": meta_dict}

        return data


if __name__ == "__main__":
    try:
        hub = Hub.model_validate(
            "  loop_d 1 o [zone=restricted color=orange max_drones=6]"
        )
    except ValidationError as e:
        ParserUtils.print_formatted_errors(e)
