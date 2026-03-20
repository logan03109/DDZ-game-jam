# scenes/next_boss_scene.py
import pygame
import math
import random

class NextBossScene:
    def __init__(self, screen, W, H, boss_index, game_state):
        self.screen     = screen
        self.W          = W
        self.H          = H
        self.boss_index = boss_index
        self.game_state = game_state   # we pass the existing game scene so state is preserved

        self.font_title  = pygame.font.SysFont("couriernew", 60, bold=True)
        self.font_sub    = pygame.font.SysFont("couriernew", 24)
        self.font_btn    = pygame.font.SysFont("couriernew", 28, bold=True)
        self.font_small  = pygame.font.SysFont("couriernew", 18)

        btn_w, btn_h = 220, 55
        self.play_btn     = pygame.Rect(self.W // 2 - btn_w // 2, self.H // 2 + 120, btn_w, btn_h)
        self.play_hovered = False

        self.tick      = 0
        self.particles = [self._new_particle() for _ in range(60)]

    def _new_particle(self):
        return {
            "x":     random.randint(0, self.W),
            "y":     random.randint(0, self.H),
            "speed": random.uniform(0.3, 1.2),
            "sym":   random.choice(["♥", "♦", "♠", "♣", "★"]),
            "col":   random.choice([(180, 30, 60), (30, 120, 200), (220, 175, 50)]),
            "size":  random.randint(14, 32),
        }

    def _draw_particles(self):
        for p in self.particles:
            font = pygame.font.SysFont("segoeui", p["size"])
            surf = font.render(p["sym"], True, p["col"])
            self.screen.blit(surf, (int(p["x"]), int(p["y"])))
            p["y"] -= p["speed"]
            if p["y"] < -40:
                p.update(self._new_particle())

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.play_hovered = self.play_btn.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.play_btn.collidepoint(event.pos):
                return self.game_state   # return existing game scene to resume

        return None

    def update(self, dt):
        self.tick += 1
        return None

    def draw(self):
        self.screen.fill((8, 12, 22))
        self._draw_particles()

        # "UP NEXT" label
        from settings import BOSS_CONFIGS
        boss = BOSS_CONFIGS[self.boss_index]

        up_next = self.font_small.render("-- UP NEXT --", True, (100, 100, 120))
        self.screen.blit(up_next, up_next.get_rect(centerx=self.W // 2, centery=self.H // 2 - 120))

        # Boss name
        pulse     = abs(math.sin(self.tick * 0.04))
        name_col  = (int(200 + pulse * 55), int(40 + pulse * 20), int(40 + pulse * 20))
        name_surf = self.font_title.render(boss["name"], True, name_col)
        self.screen.blit(name_surf, name_surf.get_rect(centerx=self.W // 2, centery=self.H // 2 - 60))

        # Boss HP
        hp_surf = self.font_sub.render(f"HP: {boss['hp']}", True, (180, 60, 60))
        self.screen.blit(hp_surf, hp_surf.get_rect(centerx=self.W // 2, centery=self.H // 2))

        # Divider line
        pygame.draw.line(self.screen, (60, 30, 30),
                         (self.W // 2 - 200, self.H // 2 + 40),
                         (self.W // 2 + 200, self.H // 2 + 40), 1)

        # Play button
        col = (0, 60, 55) if self.play_hovered else (10, 30, 28)
        pygame.draw.rect(self.screen, col, self.play_btn, border_radius=8)
        pygame.draw.rect(self.screen, (0, 220, 180), self.play_btn, 2, border_radius=8)
        label_col = (0, 220, 180) if self.play_hovered else (160, 210, 200)
        txt = self.font_btn.render("[ PLAY ]", True, label_col)
        self.screen.blit(txt, txt.get_rect(center=self.play_btn.center))