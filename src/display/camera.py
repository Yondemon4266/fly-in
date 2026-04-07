from src.models.hub import Hub


class Camera:
    def __init__(
        self, hubs: list[Hub], screen_width: int, screen_height: int
    ) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        margin = 100

        logical_xs = [hub.x for hub in hubs]
        logical_ys = [hub.y for hub in hubs]

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
        screen_x = int(logical_x * self.scale + self.offset_x)
        screen_y = int(-logical_y * self.scale + self.offset_y)
        return screen_x, screen_y
