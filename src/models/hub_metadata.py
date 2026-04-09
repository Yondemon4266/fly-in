from pydantic import (
    BaseModel,
    Field,
    model_validator,
    ValidationError,
    ConfigDict,
)
from typing import Any
from src.parser.parser_utils import ParserUtils
from enum import Enum


class ZoneType(Enum):
    """Supported zone behaviors for a hub."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class HubMetadata(BaseModel):
    """Metadata associated with a hub.

    Attributes:
        zone: Zone behavior category for routing and display logic.
        color: Optional display color name.
        max_drones: Maximum drones that can occupy the hub simultaneously.
    """

    model_config = ConfigDict(extra="forbid")

    zone: ZoneType = Field(default=ZoneType.NORMAL)
    color: str | None = Field(default=None)
    max_drones: int = Field(default=1, gt=0)

    @model_validator(mode="before")
    @classmethod
    def string_to_dict(cls, data: Any) -> Any:
        """Convert metadata string representation into a dictionary.

        Args:
            data: Raw metadata value, usually a string like
                ``[zone=priority color=red max_drones=2]``.

        Returns:
            Parsed dictionary or original input when no conversion is needed.

        Raises:
            ValueError: If input string format is invalid.
        """
        message = (
            "Invalid format for hub metadata, expected format: "
            "[key=value].\ninput: "
        )
        res: dict[str, str] = {}
        if isinstance(data, str):
            data_clean = data.strip()
            if not data_clean.startswith("[") or not data_clean.endswith("]"):
                raise ValueError(f"{message} '{data}'")

            inner_content = data_clean[1:-1].strip()

            for char in inner_content:
                if not (char.isalnum() or char in ["=", "_", " "]):
                    raise ValueError(f"{message} '{data}'")

            splitted_data = inner_content.split()
            if len(splitted_data) > 3:
                raise ValueError(f"{message} '{data}'")
            for info in splitted_data:
                splitted_info = info.split("=")
                if len(splitted_info) != 2:
                    raise ValueError(f"{message} '{data}'")
                key, value = splitted_info[0], splitted_info[1]
                if key == "color":
                    if not value.isalpha():
                        raise ValueError(
                            f"Hub metadata color must be "
                            f"a single-word color '{data}'"
                        )
                res[key] = value
            return res

        return data


if __name__ == "__main__":
    try:
        hub = HubMetadata.model_validate(
            "   [ zone=restricted color=red max_drones=2   ]"
        )
    except ValidationError as e:
        ParserUtils.print_formatted_errors(e)
