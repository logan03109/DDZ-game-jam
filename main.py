# main.py
import pygame
import sys
from settings import W, H, FPS
from scenes.menu_scene import MenuScene

def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Steampunk DDZ")
    clock = pygame.time.Clock()

    current_scene = MenuScene(screen)

    while True:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            result = current_scene.handle_event(event)
            if result:
                current_scene = result
        next_scene = current_scene.update(dt)
        if next_scene:
            current_scene = next_scene   # scene switching

        current_scene.draw()
        pygame.display.flip()

if __name__ == "__main__":
    main()