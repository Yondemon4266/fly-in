from typing import Optional


class AStarNode:
    def __init__(
        self,
        hub_name: str,
        turns_from_start: int,
        total_estimated_turns: int,
        parent: Optional["AStarNode"] = None,
    ) -> None:
        self.hub_name = hub_name
        self.turns_from_start = turns_from_start
        self.total_estimated_turns = total_estimated_turns
        self.parent = parent

    def __lt__(self, other: "AStarNode") -> bool:
        return self.total_estimated_turns < other.total_estimated_turns
