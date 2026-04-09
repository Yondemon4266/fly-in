from pydantic import (
    BaseModel,
    Field,
    model_validator,
    ValidationError,
    ConfigDict,
)
from typing import Any
from src.parser.parser_utils import ParserUtils


class ConnectionMetadata(BaseModel):
    """Metadata associated with a connection.

    Attributes:
        max_link_capacity: Maximum number of drones allowed concurrently on
            this link.
    """

    model_config = ConfigDict(extra="forbid")

    max_link_capacity: int = Field(default=1, gt=0)

    @model_validator(mode="before")
    @classmethod
    def string_to_dict(cls, data: Any) -> Any:
        """Convert metadata string representation into a dictionary.

        Args:
            data: Raw metadata value, usually a string like
                ``[max_link_capacity=3]``.

        Returns:
            Parsed dictionary or original input when no conversion is needed.

        Raises:
            ValueError: If input string format is invalid.
        """
        message = (
            "Invalid format for connection metadata, expected format: "
            "[key=value].\ninput: "
        )
        if isinstance(data, str):
            data_clean = data.strip()
            if not data_clean.startswith("[") and not data_clean.endswith("]"):
                raise ValueError(f"{message} '{data}'")

            inner_content = data_clean[1:-1].strip()
            for char in inner_content:
                if not (char.isalnum() or char in ["=", "_", " "]):
                    raise ValueError(f"{message} '{data}'")
            splitted_data = inner_content.split()
            if len(splitted_data) != 1:
                raise ValueError(f"{message} '{data}'")
            res = splitted_data[0].split("=")
            if len(res) != 2:
                raise ValueError(f"{message} '{data}'")
            key, value = res[0], res[1]
            return {key: value}
        return data


if __name__ == "__main__":
    try:
        connection = ConnectionMetadata.model_validate(
            "  [max_link_capacity=1000 ]"
        )
        print(connection.max_link_capacity)
    except ValidationError as e:
        ParserUtils.print_formatted_errors(e)
