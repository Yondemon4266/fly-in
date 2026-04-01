from pydantic import ValidationError
import sys


class ParserUtils:

    @staticmethod
    def print_formatted_errors(e: ValidationError, line: int) -> None:
        sys.stderr.write("\n")
        for err in e.errors():
            field_name = (
                " -> ".join(str(loc) for loc in err["loc"])
                if err["loc"]
                else "global"
            )
            sys.stderr.write(
                f"[Parsing {field_name} error]: at line {line}:"
                f" {err['msg']}\n\n"
            )
