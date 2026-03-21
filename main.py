# main.py
import pygame
import sys
from settings import FPS
from scenes.menu_scene import MenuScene



def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.RESIZABLE)
    W, H = screen.get_size()
    pygame.display.set_caption("The Eye")
    clock = pygame.time.Clock()

    current_scene = MenuScene(screen, W, H)
    fullscreen = True  # track state, starts fullscreen

    while True:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.RESIZABLE)
                    else:
                        screen = pygame.display.set_mode((1280, 800), pygame.RESIZABLE)
                    W, H = screen.get_size()
                    if hasattr(current_scene, 'on_resize'):
                        current_scene.on_resize(W, H)
            if event.type == pygame.VIDEORESIZE:
                W, H = event.w, event.h
                screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
                if hasattr(current_scene, 'on_resize'):
                    current_scene.on_resize(W, H)

            result = current_scene.handle_event(event)
            if result:
                current_scene = result

            # check windowed request immediately after handle_event
            if hasattr(current_scene, 'request_windowed') and current_scene.request_windowed:
                current_scene.request_windowed = False
                fullscreen = False
                screen = pygame.display.set_mode((1280, 800), pygame.NOFRAME)
                W, H = screen.get_size()
                current_scene.screen = screen
                if hasattr(current_scene, 'on_resize'):
                    current_scene.on_resize(W, H)

        next_scene = current_scene.update(dt)
        if next_scene:
            current_scene = next_scene

        current_scene.draw()
        pygame.display.flip()

if __name__ == "__main__":
    main()