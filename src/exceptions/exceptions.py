class FlyInError(Exception):
    def __init__(self, message="Error on fly-in simulation") -> None:
        self.message = message
        super().__init__(self.message)


class ParsingError(FlyInError):
    def __init__(
        self, message="Error on parsing the map", line: int | None = None
    ) -> None:
        self.message = message
        self.line = line
        if self.line is not None:
            self.message = f"Parsing error on line {self.line}: {message}"
        else:
            self.message = f"Parsing error: {message}"
        super().__init__(self.message)
