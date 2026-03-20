# scenes/settings_scene.py
import pygame
import math
import random

class SettingsScene:
    # noinspection PyPep8Naming
    def __init__(self, screen, W, H, previous_scene):
        self.screen          = screen
        self.W               = W
        self.H               = H
        self.previous_scene  = previous_scene  # scene to return to

        self.font_title = pygame.font.SysFont("couriernew", 60, bold=True)
        self.font_btn   = pygame.font.SysFont("couriernew", 26, bold=True)
        self.font_small = pygame.font.SysFont("couriernew", 16)

        self.tick      = 0
        self.particles = [self._new_particle() for _ in range(40)]

        btn_w, btn_h = 300, 55
        self.windowed_btn = pygame.Rect(self.W // 2 - btn_w // 2, self.H // 2 - 60,  btn_w, btn_h)
        self.menu_btn     = pygame.Rect(self.W // 2 - btn_w // 2, self.H // 2 + 20,  btn_w, btn_h)
        self.exit_btn     = pygame.Rect(self.W // 2 - btn_w // 2, self.H // 2 + 100, btn_w, btn_h)

        self.windowed_hovered = False
        self.menu_hovered     = False
        self.exit_hovered     = False
        self.request_windowed = False

    def _new_particle(self):
        return {
            "x":     random.randint(0, self.W),
            "y":     random.randint(0, self.H),
            "speed": random.uniform(0.3, 1.0),
            "sym":   random.choice(["♥", "♦", "♠", "♣", "★"]),
            "col":   random.choice([(60, 60, 100), (40, 80, 120), (80, 60, 100)]),
            "size":  random.randint(14, 28),
        }

    def _draw_particles(self):
        for p in self.particles:
            font = pygame.font.SysFont("segoeui", p["size"])
            surf = font.render(p["sym"], True, p["col"])
            self.screen.blit(surf, (int(p["x"]), int(p["y"])))
            p["y"] -= p["speed"]
            if p["y"] < -40:
                p.update(self._new_particle())

    def _draw_button(self, rect, text, hovered, border_col, hover_col):
        col = hover_col if hovered else (10, 10, 20)
        pygame.draw.rect(self.screen, col,        rect, border_radius=8)
        pygame.draw.rect(self.screen, border_col, rect, 2, border_radius=8)
        pulse     = abs(math.sin(self.tick * 0.05))
        label_col = tuple(min(255, int(c * (0.7 + 0.3 * pulse))) for c in border_col)
        txt = self.font_btn.render(text, True, label_col)
        self.screen.blit(txt, txt.get_rect(center=rect.center))

    # noinspection PyPep8Naming
    def on_resize(self, W, H):
        self.W = W
        self.H = H
        btn_w, btn_h = 300, 55
        self.windowed_btn = pygame.Rect(self.W // 2 - btn_w // 2, self.H // 2 - 60,  btn_w, btn_h)
        self.menu_btn     = pygame.Rect(self.W // 2 - btn_w // 2, self.H // 2 + 20,  btn_w, btn_h)
        self.exit_btn     = pygame.Rect(self.W // 2 - btn_w // 2, self.H // 2 + 100, btn_w, btn_h)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.windowed_hovered = self.windowed_btn.collidepoint(event.pos)
            self.menu_hovered     = self.menu_btn.collidepoint(event.pos)
            self.exit_hovered     = self.exit_btn.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.windowed_btn.collidepoint(event.pos):
                # signal main.py to switch to windowed
                self.request_windowed = True
                return None
            if self.menu_btn.collidepoint(event.pos):
                from scenes.menu_scene import MenuScene
                return MenuScene(self.screen, self.W, self.H)
            if self.exit_btn.collidepoint(event.pos):
                import sys
                pygame.quit()
                sys.exit()

        return None

    def update(self, dt):
        self.tick += 1
        return None

    def draw(self):
        self.screen.fill((8, 10, 20))
        self._draw_particles()

        # Title
        title = self.font_title.render("SETTINGS", True, (180, 180, 220))
        self.screen.blit(title, title.get_rect(centerx=self.W // 2, centery=self.H // 2 - 160))

        # Divider
        pygame.draw.line(self.screen, (50, 50, 80),
                         (self.W // 2 - 200, self.H // 2 - 100),
                         (self.W // 2 + 200, self.H // 2 - 100), 1)

        self._draw_button(self.windowed_btn, "[ BORDERLESS WINDOW ]",
                          self.windowed_hovered, (0, 180, 220),  (0, 50, 70))
        self._draw_button(self.menu_btn,     "[ MAIN MENU ]",
                          self.menu_hovered,     (220, 175, 50), (60, 45, 0))
        self._draw_button(self.exit_btn,     "[ EXIT ]",
                          self.exit_hovered,     (210, 50, 50),  (60, 10, 10))