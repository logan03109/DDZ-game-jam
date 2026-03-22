import pygame
import math
import random
from settings import resource_path, FONT_SIZE_SMALL, FONT_SIZE_TITLE

class CreditsScene:
    def __init__(self, screen, W, H):
        self.screen = screen
        self.W      = W
        self.H      = H

        self.font_title = pygame.font.SysFont("couriernew", FONT_SIZE_TITLE, bold=True)
        self.font_text  = pygame.font.SysFont("couriernew", FONT_SIZE_SMALL)
        self.font_btn   = pygame.font.SysFont("couriernew", 26, bold=True)

        self.tick      = 0
        self.particles = [self._new_particle() for _ in range(40)]

        btn_w, btn_h   = 220, 55
        self.back_btn  = pygame.Rect(self.W // 2 - btn_w // 2, self.H - 100, btn_w, btn_h)
        self.back_hovered = False

        # ── WRITE YOUR CREDITS HERE ──────────────────────────
        self.lines = [
            ("Project Leader",    (220, 175, 50)),
            ("Logan", (180, 180, 200)),
            ("",               (0, 0, 0)),
            ("PROGRAMMING",    (220, 175, 50)),
            ("In.Dev(Devin), Triple Tom(Tom)", (180, 180, 200)),
            ("",               (0, 0, 0)),
            ("ART",            (220, 175, 50)),
            ("A_jy.w(Amy)", (180, 180, 200)),
            ("",               (0, 0, 0)),
            ("MUSIC",          (220, 175, 50)),
            ("GDLT(Royce), MiniNav(Ashwin)", (180, 180, 200)),
            ("",               (0, 0, 0)),
        ]
        # ────────────────────────────────────────────────────

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

    def on_resize(self, W, H):
        self.W       = W
        self.H       = H
        btn_w, btn_h = 220, 55
        self.back_btn = pygame.Rect(self.W // 2 - btn_w // 2, self.H - 100, btn_w, btn_h)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.back_hovered = self.back_btn.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_btn.collidepoint(event.pos):
                from scenes.menu_scene import MenuScene
                return MenuScene(self.screen, self.W, self.H)
        return None

    def update(self, dt):
        self.tick += 1
        return None

    def draw(self):
        self.screen.fill((8, 10, 20))
        self._draw_particles()

        title = self.font_title.render("CREDITS", True, (180, 180, 220))
        self.screen.blit(title, title.get_rect(
            centerx=self.W // 2, centery=120))

        pygame.draw.line(self.screen, (50, 50, 80),
                         (self.W // 2 - 200, 165),
                         (self.W // 2 + 200, 165), 1)

        start_y = 200
        for text, col in self.lines:
            if text:
                surf = self.font_text.render(text, True, col)
                self.screen.blit(surf, surf.get_rect(
                    centerx=self.W // 2, top=start_y))
            start_y += 30

        # back button
        pulse     = abs(math.sin(self.tick * 0.05))
        bg_col    = (60, 45, 0) if self.back_hovered else (10, 10, 20)
        border_col = (220, 175, 50)
        label_col = tuple(min(255, int(c * (0.7 + 0.3 * pulse))) for c in border_col)
        pygame.draw.rect(self.screen, bg_col,     self.back_btn, border_radius=8)
        pygame.draw.rect(self.screen, border_col, self.back_btn, 2, border_radius=8)
        txt = self.font_btn.render("[ BACK ]", True, label_col)
        self.screen.blit(txt, txt.get_rect(center=self.back_btn.center))