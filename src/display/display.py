import pygame
from src.display.drone import Drone
from src.models.hub import Hub
from src.display.camera import Camera


class DisplayPygameFlyin:
    def __init__(self, drones: list[Drone], hubs: list[Hub]) -> None:
        self.drones = drones
        self.hubs = hubs
        self.screen = pygame.display.set_mode((1280, 720))
        self.camera = Camera(self.hubs, self.screen.width, self.screen.height)
        clock = pygame.time.Clock()
        dt = 0
        running = True

        while running:
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        running = False
                    case pygame.WINDOWSIZECHANGED:
                        self.camera = Camera(self.hubs, event.x, event.y)

                

            self.screen.fill("purple")
            for hub in self.hubs:
                centered_pos = self.camera.get_screen_coords(hub.x, hub.y)
                pygame.draw.circle(
                    self.screen, "red", centered_pos, self.camera.hub_radius
                )
            pygame.display.flip()
            dt = clock.tick(60) / 1000
        pygame.quit()
