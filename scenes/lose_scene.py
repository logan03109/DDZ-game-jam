# scenes/lose_scene.py
import pygame
import math
import random

class LoseScene:
    def __init__(self, screen, W, H):
        self.screen = screen
        self.W = W
        self.H = H

        self.font_title = pygame.font.SysFont("couriernew", 80, bold=True)
        self.font_sub   = pygame.font.SysFont("couriernew", 20)
        self.font_btn   = pygame.font.SysFont("couriernew", 26, bold=True)

        btn_w, btn_h = 220, 55
        self.new_game_btn = pygame.Rect(self.W // 2 - btn_w - 20, self.H // 2 + 80, btn_w, btn_h)
        self.menu_btn     = pygame.Rect(self.W // 2 + 20,          self.H // 2 + 80, btn_w, btn_h)
        self.new_game_hovered = False
        self.menu_hovered     = False

        self.tick      = 0
        self.particles = [self._new_particle() for _ in range(80)]

    def _new_particle(self):
        return {
            "x":     random.randint(0, self.W),
            "y":     random.randint(0, self.H),
            "speed": random.uniform(0.5, 2.0),
            "sym":   random.choice(["♥", "♦", "♠", "♣", "★"]),
            "col":   random.choice([(200, 40, 40), (120, 20, 20), (80, 10, 10)]),
            "size":  random.randint(16, 36),
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
        col = hover_col if hovered else (10, 10, 10)
        pygame.draw.rect(self.screen, col,        rect, border_radius=8)
        pygame.draw.rect(self.screen, border_col, rect, 2, border_radius=8)
        pulse     = abs(math.sin(self.tick * 0.05))
        label_col = tuple(min(255, int(c * (0.7 + 0.3 * pulse))) for c in border_col)
        txt = self.font_btn.render(text, True, label_col)
        self.screen.blit(txt, txt.get_rect(center=rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.new_game_hovered = self.new_game_btn.collidepoint(event.pos)
            self.menu_hovered     = self.menu_btn.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.new_game_btn.collidepoint(event.pos):
                from scenes.game_scene import GameScene
                return GameScene(self.screen, self.W, self.H)
            if self.menu_btn.collidepoint(event.pos):
                from scenes.menu_scene import MenuScene
                return MenuScene(self.screen, self.W, self.H)

        return None

    def update(self, dt):
        self.tick += 1
        return None

    def draw(self):
        self.screen.fill((8, 5, 5))
        self._draw_particles()

        # Title
        pulse = abs(math.sin(self.tick * 0.03))
        col   = (int(180 + pulse * 40), int(20 + pulse * 20), int(20 + pulse * 20))
        title = self.font_title.render("YOU LOSE", True, col)
        self.screen.blit(title, title.get_rect(centerx=self.W // 2, centery=self.H // 2 - 80))

        # Subtitle
        sub = self.font_sub.render("You ran out of plays. The Shadow Landlord wins.", True, (160, 80, 80))
        self.screen.blit(sub, sub.get_rect(centerx=self.W // 2, centery=self.H // 2))

        # Buttons
        self._draw_button(self.new_game_btn, "[ NEW GAME ]",
                          self.new_game_hovered, (210, 50, 50), (60, 10, 10))
        self._draw_button(self.menu_btn,     "[ MENU ]",
                          self.menu_hovered,     (220, 175, 50), (60, 45, 0))