class FlyinError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class ParsingError(FlyinError):
    def __init__(self, message: str, line: int):
        super().__init__(f"[Parsing error] at line {line} {message}")
