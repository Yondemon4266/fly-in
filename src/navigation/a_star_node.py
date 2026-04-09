from typing import Optional


class AStarNode:
    """Search node used by the A* planner.

    Attributes:
        hub_name: Current hub name for this state.
        turns_from_start: Accumulated turns from start.
        total_estimated_turns: A* score ``g + h`` for priority ordering.
        parent: Previous node used to reconstruct final path.
    """

    def __init__(
        self,
        hub_name: str,
        turns_from_start: int,
        total_estimated_turns: int,
        parent: Optional["AStarNode"] = None,
    ) -> None:
        """Create a new A* node.

        Args:
            hub_name: Current hub name.
            turns_from_start: Cost from start in turns.
            total_estimated_turns: Estimated total turns to goal.
            parent: Previous node in the path.
        """
        self.hub_name = hub_name
        self.turns_from_start = turns_from_start
        self.total_estimated_turns = total_estimated_turns
        self.parent = parent

    def __lt__(self, other: "AStarNode") -> bool:
        """Order nodes for heap priority.

        Args:
            other: Node to compare against.

        Returns:
            ``True`` when this node has higher search priority.
        """
        if self.total_estimated_turns == other.total_estimated_turns:
            return self.turns_from_start > other.turns_from_start
        return self.total_estimated_turns < other.total_estimated_turns
