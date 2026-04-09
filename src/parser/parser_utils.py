from pydantic import ValidationError
import sys


class ParserUtils:
    """Utility helpers shared by parser components."""

    @staticmethod
    def print_formatted_errors(e: ValidationError) -> None:
        """Print pydantic validation errors in a parser-friendly format.

        Args:
            e: Validation error raised by pydantic models.
        """
        sys.stderr.write("\n")
        for err in e.errors():
            field_name = (
                " -> ".join(str(loc) for loc in err["loc"])
                if err["loc"]
                else "global"
            )
            sys.stderr.write(
                f"[Parsing {field_name} error]:" f" {err['msg']}\n\n"
            )
