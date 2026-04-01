from pydantic import (
    BaseModel,
    Field,
    model_validator,
    ValidationError,
    ConfigDict,
)
from typing import Any
from src.parser.parser_utils import ParserUtils
from src.parser.models.connection_metadata import ConnectionMetadata


class Connection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hub_a: str = Field(...)
    hub_b: str = Field(...)
    metadata: ConnectionMetadata = Field(default_factory=ConnectionMetadata)

    @model_validator(mode="before")
    @classmethod
    def string_to_dict(cls, data: Any) -> Any:
        message = (
            "Invalid format for connection, expected format: "
            "name1-name2 [key=value].\ninput: "
        )
        if isinstance(data, str):
            data_clean = data.strip()
            name_part = data_clean
            meta_dict = {}

            if "[" in data_clean:
                parts = data_clean.split("[")
                if len(parts) != 2:
                    raise ValueError(f"{message} {data}")
                name_part = parts[0].strip()
                meta_dict = "[" + parts[1].strip()

            hubs = name_part.split("-")
            if len(hubs) != 2:
                raise ValueError(
                    "Connection must contain " f"only one '-' {name_part}"
                )

            name1, name2 = hubs[0], hubs[1]

            for n in [name1, name2]:
                if not n:
                    raise ValueError(
                        f"Hub name can't be empty in connection: '{name_part}'"
                    )
                if " " in n:
                    raise ValueError(f"Hub name '{n}' cannot contain spaces.")
            return {"hub_a": name1, "hub_b": name2, "metadata": meta_dict}

        return data


if __name__ == "__main__":
    try:
        connection = Connection.model_validate(
            "   start-gate1 [max_link_capacity=20]   "
        )

        print(connection)
    except ValidationError as e:
        ParserUtils.print_formatted_errors(e)
