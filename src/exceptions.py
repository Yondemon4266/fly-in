class FlyinError(Exception):
    """Base exception for all Fly-in domain errors."""

    def __init__(self, message: str) -> None:
        """Initialize the exception with a human-readable message.

        Args:
            message: Error details to expose to callers.
        """
        super().__init__(message)


class ParsingError(FlyinError):
    """Raised when map parsing fails due to invalid input format or content."""

    def __init__(self, message: str, line: int | None = None) -> None:
        """Build a parsing error message with optional line information.

        Args:
            message: Error details for the invalid parsed content.
            line: Optional source line number where the error occurred.
        """
        if line:
            super().__init__(f"[Parsing error] at line {line} {message}")
        else:
            super().__init__(f"[Parsing error] {message}")


class PathNotFoundError(FlyinError):
    """Raised when no valid route can be found between hubs."""

    def __init__(self, message: str) -> None:
        """Build a path-not-found error message.

        Args:
            message: Error details for why path computation failed.
        """
        super().__init__(f"[Path not found error] {message}")


class ConnectionNotFoundError(FlyinError):
    """Raised when a required connection cannot be resolved."""

    def __init__(self, message: str) -> None:
        """Build a connection-not-found error message.

        Args:
            message: Error details for the missing connection.
        """
        super().__init__(f"[Connection not found error] {message}")
