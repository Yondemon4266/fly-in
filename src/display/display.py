import pygame
from src.display.drone import Drone, DroneState
from src.models.hub import Hub
from src.models.hub_metadata import ZoneType
from src.display.camera import Camera
from src.models.connection import Connection
import math


class DisplayPygameFlyin:
    def __init__(
        self,
        drones: list[Drone],
        hubs: list[Hub],
        connections: list[Connection],
    ) -> None:
        self.drones = drones
        self.hubs = self._init_hubs_dict(hubs)
        self.connections = connections
        self.screen = pygame.display.set_mode((1280, 720))
        self.camera = Camera(self.hubs, self.screen.width, self.screen.height)
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.running = True
        self.bg_color = (33, 33, 33)
        pygame.font.init()
        self.font = pygame.font.SysFont("Trebuchet MS", 14, bold=True)
        self.original_drone_img = pygame.image.load(
            "assets/drone.png"
        ).convert_alpha()

        self.current_drone_img = self.original_drone_img
        self._update_drone_image_size()
        self.turn_duration = 650
        self.current_turn = 0
        self.turn_progress = 0
        self.pause_at_turn = -1
        self.advancing = True
        self.is_playing = False
        self.max_turn = max(
            max(
                drone.timeline.keys()
                for drone in self.drones
                if drone.timeline
            )
        )
        while self.running:
            if self.is_playing:
                self._advance_turn_time()
            self._event_handler()
            self.screen.fill(self.bg_color)
            self._draw_connections()
            self._draw_hubs()
            self._draw_drones()
            self._display_fps()
            self._display_top_right_info()
            pygame.display.flip()
            self.dt = self.clock.tick(60)
        pygame.quit()

    def _init_hubs_dict(self, list_hubs: list[Hub]) -> dict[str, Hub]:
        created_hubs: dict[str, Hub] = {}
        for hub in list_hubs:
            created_hubs[hub.name] = hub
        return created_hubs

    def _advance_turn_time(self) -> None:
        if self.advancing:
            self.turn_progress += self.dt
            if self.turn_progress >= self.turn_duration:
                self.current_turn += 1
                self.turn_progress = 0

                if (
                    self.current_turn == self.pause_at_turn
                    or self.current_turn >= self.max_turn
                ):
                    self.is_playing = False
                    self.pause_at_turn = -1

        else:
            self.turn_progress -= self.dt
            if self.turn_progress <= 0:
                self.turn_progress = 0

                if (
                    self.current_turn == self.pause_at_turn
                    or self.current_turn == 0
                ):
                    self.is_playing = False
                    self.pause_at_turn = -1

    def _event_handler(self) -> None:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
                case pygame.WINDOWSIZECHANGED:
                    self.camera = Camera(self.hubs, event.x, event.y)
                    self._update_drone_image_size()
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_q | pygame.K_ESCAPE:
                            self.running = False
                        case pygame.K_p:
                            if self.current_turn >= self.max_turn:
                                self.current_turn = 0
                            self.is_playing = not self.is_playing
                            self.advancing = True
                        case pygame.K_RIGHT:
                            if (
                                not self.is_playing
                                and self.current_turn < self.max_turn
                            ):
                                self.advancing = True
                                self.is_playing = True
                                self.pause_at_turn = self.current_turn + 1
                        case pygame.K_LEFT:
                            if not self.is_playing and self.current_turn > 0:
                                self.advancing = False
                                self.is_playing = True
                                self.current_turn -= 1
                                self.turn_progress = self.turn_duration
                                self.pause_at_turn = self.current_turn

    def _display_fps(self) -> None:
        fps = int(self.clock.get_fps())
        fps_surface = self.font.render(f"FPS: {fps}", True, (255, 255, 255))
        fps_rect = fps_surface.get_rect(topleft=(10, 10))
        self.screen.blit(fps_surface, fps_rect)

    def _display_top_right_info(self) -> None:
        screen_width = self.screen.get_width()

        line1_surface = self.font.render(
            f"Current turn: {self.current_turn}", True, (255, 255, 255)
        )
        line1_rect = line1_surface.get_rect(topright=(screen_width - 10, 10))
        self.screen.blit(line1_surface, line1_rect)

        line2_surface = self.font.render(
            f"Resolved in: {self.max_turn} turns", True, (255, 255, 255)
        )
        line2_rect = line2_surface.get_rect(
            topright=(screen_width - 10, line1_rect.bottom + 5)
        )
        self.screen.blit(line2_surface, line2_rect)

    def _draw_hubs(self) -> None:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for hub in self.hubs.values():
            centered_pos = self.camera.get_screen_coords(hub.x, hub.y)
            safe_color = self._get_valid_color(hub.metadata.color)
            border_color, border_thickness = self._get_zone_border(
                hub.metadata.zone
            )
            pygame.draw.circle(
                self.screen,
                border_color,
                centered_pos,
                self.camera.hub_radius + border_thickness,
            )
            pygame.draw.circle(
                self.screen,
                safe_color,
                centered_pos,
                self.camera.hub_radius,
            )

            if (
                hub.metadata.max_drones > 1
                and hub.metadata.zone.value != "blocked"
            ):
                capacity_surface = self.font.render(
                    str(hub.metadata.max_drones), True, (255, 255, 255)
                )
                capacity_rect = capacity_surface.get_rect(center=centered_pos)
                self.screen.blit(capacity_surface, capacity_rect)

            dx = mouse_x - centered_pos[0]
            dy = mouse_y - centered_pos[1]
            distance = math.sqrt(dx**2 + dy**2)
            if distance <= self.camera.hub_radius + border_thickness:
                text_surface = self.font.render(
                    hub.name, True, (255, 255, 255)
                )

                offset_y = self.camera.hub_radius + 20
                text_rect = text_surface.get_rect(
                    center=(centered_pos[0], centered_pos[1] - offset_y)
                )

                self.screen.blit(text_surface, text_rect)

    def _draw_connections(self) -> None:
        for connection in self.connections:
            hub_a = self.hubs[connection.hub_a]
            hub_b = self.hubs[connection.hub_b]

            x_a, y_a = self.camera.get_screen_coords(hub_a.x, hub_a.y)
            x_b, y_b = self.camera.get_screen_coords(hub_b.x, hub_b.y)

            dx = x_b - x_a
            dy = y_b - y_a

            distance = math.sqrt(dx**2 + dy**2)
            if distance == 0:
                continue
            dir_x = dx / distance
            dir_y = dy / distance
            offset = self.camera.hub_radius - 1
            if distance <= offset * 2:
                continue
            start_x = int(x_a + (dir_x * offset))
            start_y = int(y_a + (dir_y * offset))

            end_x = int(x_b - (dir_x * offset))
            end_y = int(y_b - (dir_y * offset))
            thickness = max(2, int(self.camera.hub_radius * 0.75))
            line_color = (180, 180, 180)
            pygame.draw.line(
                self.screen,
                line_color,
                (start_x, start_y),
                (end_x, end_y),
                thickness,
            )

    def _draw_drones(self) -> None:

        lerp_factor = self.turn_progress / max(self.turn_duration, 1)

        for drone in self.drones:
            x_a, y_a = self._get_logical_pos_at_turn(drone, self.current_turn)

            x_b, y_b = self._get_logical_pos_at_turn(
                drone, self.current_turn + 1
            )

            current_x = x_a + (x_b - x_a) * lerp_factor
            current_y = y_a + (y_b - y_a) * lerp_factor

            pos = self.camera.get_screen_coords(current_x, current_y)
            drone_rect = self.current_drone_img.get_rect(center=pos)
            self.screen.blit(self.current_drone_img, drone_rect)

    def _update_drone_image_size(self) -> None:
        size = int(self.camera.drone_radius * 8)

        self.current_drone_img = pygame.transform.smoothscale(
            self.original_drone_img, (size, size)
        )

    def _get_logical_pos_at_turn(
        self, drone: Drone, turn: int
    ) -> tuple[float, float]:
        info = drone.get_state_at(turn)
        hub = self.hubs[info.hub]

        if info.state in (DroneState.ON_HUB, DroneState.ARRIVED):
            return (hub.x, hub.y)

        elif info.state == DroneState.IN_TRANSIT:
            hub_from = self.hubs[str(info.from_hub)]

            mid_x = (hub_from.x + hub.x) / 2
            mid_y = (hub_from.y + hub.y) / 2
            return (mid_x, mid_y)
        else:
            return (hub.x, hub.y)

    def _get_zone_border(
        self, zone_type: ZoneType
    ) -> tuple[tuple[int, int, int], int]:
        # On utilise .value pour récupérer la chaîne de caractères de l'Enum ('restricted', etc.)
        match zone_type.value:
            case "restricted":
                return (255, 140, 0), 6  # Un contour Orange épais
            case "priority":
                return (50, 205, 50), 6  # Un contour Vert brillant épais
            case "blocked":
                return (220, 20, 60), 6  # Un contour Rouge intense épais
            case _:  # "normal" ou autre
                return (150, 150, 150), 4  # Un contour Gris classique et fin

    def _get_valid_color(self, color_name: str | None) -> str:
        if not color_name:
            return "gray"

        try:
            pygame.Color(color_name)
            return color_name
        except ValueError:
            return "gray"
