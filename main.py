# main.py
import pygame
import sys
from settings import FPS
from scenes.menu_scene import MenuScene

def main():
    pygame.init()
    info = pygame.display.Info()
    W, H = info.current_w, info.current_h
    screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
    pygame.display.set_caption("Steampunk DDZ")
    clock = pygame.time.Clock()

    current_scene = MenuScene(screen, W, H)

    while True:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # ESC exits fullscreen
                    pygame.quit()
                    sys.exit()
            result = current_scene.handle_event(event)
            if result:
                current_scene = result

        next_scene = current_scene.update(dt)  # capture this
        if next_scene:
            current_scene = next_scene

        current_scene.draw()
        pygame.display.flip()

if __name__ == "__main__":
    main()