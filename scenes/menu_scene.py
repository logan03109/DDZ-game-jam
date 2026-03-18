# scenes/menu_scene.py
import pygame
import math
import random
from settings import W, H, BG_COLOUR

class MenuScene:
    def __init__(self, screen):
        self.screen = screen

        # Fonts
        self.font_title  = pygame.font.SysFont("couriernew", 72, bold=True)
        self.font_sub    = pygame.font.SysFont("couriernew", 18)
        self.font_btn    = pygame.font.SysFont("couriernew", 28, bold=True)

        # Button
        btn_w, btn_h = 240, 60
        self.btn_rect = pygame.Rect(
            (W - btn_w) // 2,
            H // 2 + 60,
            btn_w, btn_h
        )
        self.btn_hovered = False

        # Animation state
        self.tick        = 0          # frame counter for animations
        self.glitch_tick = 0          # countdown until next glitch frame
        self.glitch_on   = False
        self.particles   = [self._new_particle() for _ in range(60)]

    # ── helpers ───────────────────────────────────────────────
    def _new_particle(self):
        """A small drifting card-suit symbol in the background."""
        return {
            "x":     random.randint(0, W),
            "y":     random.randint(0, H),
            "speed": random.uniform(0.3, 1.2),
            "sym":   random.choice(["♥", "♦", "♠", "♣"]),
            "col":   random.choice([(180,30,60,80), (30,120,200,80)]),
            "size":  random.randint(14, 32),
        }

    def _draw_particles(self):
        for p in self.particles:
            font = pygame.font.SysFont("segoeui", p["size"])
            col  = p["col"][:3]          # drop alpha for now
            surf = font.render(p["sym"], True, col)
            self.screen.blit(surf, (int(p["x"]), int(p["y"])))
            p["y"] -= p["speed"]
            if p["y"] < -40:
                p.update(self._new_particle())

    def _draw_title(self):
        """Title with cyan/magenta glitch offset on alternate frames."""
        title = "STEAMPUNK DDZ"
        offset = 4 if self.glitch_on else 0

        # Cyan ghost
        s1 = self.font_title.render(title, True, (0, 255, 220))
        r1 = s1.get_rect(centerx=W//2 + offset, centery=H//2 - 120)
        s1.set_alpha(120)
        self.screen.blit(s1, r1)

        # Magenta ghost
        s2 = self.font_title.render(title, True, (255, 0, 120))
        r2 = s2.get_rect(centerx=W//2 - offset, centery=H//2 - 120)
        s2.set_alpha(120)
        self.screen.blit(s2, r2)

        # Main white text
        s3 = self.font_title.render(title, True, (230, 225, 210))
        r3 = s3.get_rect(centerx=W//2, centery=H//2 - 120)
        self.screen.blit(s3, r3)

        # Subtitle
        sub = self.font_sub.render(">> FIGHT THE LANDLORD  //  STEAMPUNK EDITION <<", True, (80, 180, 160))
        self.screen.blit(sub, sub.get_rect(centerx=W//2, centery=H//2 - 60))

    def _draw_button(self):
        hover = self.btn_hovered

        # Glow behind button when hovered
        if hover:
            glow = pygame.Surface((self.btn_rect.w + 30, self.btn_rect.h + 30), pygame.SRCALPHA)
            pygame.draw.rect(glow, (0, 220, 180, 40), glow.get_rect(), border_radius=12)
            self.screen.blit(glow, (self.btn_rect.x - 15, self.btn_rect.y - 15))

        # Button body
        body_col = (0, 60, 55) if hover else (10, 30, 28)
        pygame.draw.rect(self.screen, body_col, self.btn_rect, border_radius=8)

        # Animated border: cycles through a neon teal
        pulse = abs(math.sin(self.tick * 0.05))
        border_col = (
            int(0   + pulse * 0),
            int(180 + pulse * 75),
            int(160 + pulse * 95),
        )
        pygame.draw.rect(self.screen, border_col, self.btn_rect, 2, border_radius=8)

        # Corner accents (cyberpunk detail)
        c = border_col
        L = 10
        for dx, dy, sx, sy in [(-1,-1,1,1),(1,-1,-1,1),(-1,1,1,-1),(1,1,-1,-1)]:
            cx = self.btn_rect.centerx + dx * self.btn_rect.w // 2
            cy = self.btn_rect.centery + dy * self.btn_rect.h // 2
            pygame.draw.line(self.screen, c, (cx, cy), (cx + sx*L, cy), 2)
            pygame.draw.line(self.screen, c, (cx, cy), (cx, cy + sy*L), 2)

        # Label
        label_col = (0, 230, 200) if hover else (160, 210, 200)
        txt = self.font_btn.render("[ PLAY ]", True, label_col)
        self.screen.blit(txt, txt.get_rect(center=self.btn_rect.center))

    def _draw_scanlines(self):
        """Subtle horizontal scanline overlay for CRT feel."""
        for y in range(0, H, 4):
            pygame.draw.line(self.screen, (0, 0, 0), (0, y), (W, y))
            # draw_line with alpha isn't straightforward in pygame,
            # so we use a pre-built surface instead — see __init__ tip below

    # ── scene interface ───────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.btn_hovered = self.btn_rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_rect.collidepoint(event.pos):
                # Import here to avoid circular imports at module level
                from scenes.game_scene import GameScene
                return GameScene(self.screen)   # signal scene change

        return None   # stay on this scene

    def update(self, dt):
        self.tick += 1

        # Glitch: fires randomly, lasts 2 frames
        self.glitch_tick -= 1
        if self.glitch_tick <= 0:
            self.glitch_on   = random.random() < 0.08   # 8% chance per frame
            self.glitch_tick = random.randint(3, 12)

        return None   # no scene transition from update (button handles it)

    def draw(self):
        self.screen.fill((8, 12, 22))   # very dark navy, not pure black
        self._draw_particles()
        self._draw_title()
        self._draw_button()