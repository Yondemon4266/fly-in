from src.models.hub import Hub


class Camera:
    """Coordinate transformer from logical map space to screen space."""

    def __init__(
        self, hubs: dict[str, Hub], screen_width: int, screen_height: int
    ) -> None:
        """Fit map bounds into the current viewport with margins.

        Args:
            hubs: Hubs used to compute logical world bounds.
            screen_width: Current screen width in pixels.
            screen_height: Current screen height in pixels.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        margin = 50

        logical_xs = [hub.x for hub in hubs.values()]
        logical_ys = [hub.y for hub in hubs.values()]

        min_x, max_x = min(logical_xs), max(logical_xs)
        min_y, max_y = min(logical_ys), max(logical_ys)

        logical_width = max_x - min_x
        logical_height = max_y - min_y

        if logical_width == 0:
            logical_width = 1
        if logical_height == 0:
            logical_height = 1

        scale_x = (self.screen_width - 2 * margin) / logical_width
        scale_y = (self.screen_height - 2 * margin) / logical_height

        self.scale = min(scale_x, scale_y)

        self.hub_radius = min(int(self.scale * 0.2), margin - 20)
        self.drone_radius = min(int(self.scale * 0.1), margin - 25)
        center_logical_x = (min_x + max_x) / 2
        center_logical_y = (min_y + max_y) / 2

        self.offset_x = (self.screen_width / 2) - (
            center_logical_x * self.scale
        )
        self.offset_y = (self.screen_height / 2) - (
            -center_logical_y * self.scale
        )

    def get_screen_coords(
        self, logical_x: float, logical_y: float
    ) -> tuple[int, int]:
        """Project logical coordinates into screen pixel coordinates.

        Args:
            logical_x: Logical x coordinate.
            logical_y: Logical y coordinate.

        Returns:
            Tuple of integer screen coordinates.
        """
        screen_x = int(logical_x * self.scale + self.offset_x)
        screen_y = int(-logical_y * self.scale + self.offset_y)
        return screen_x, screen_y
