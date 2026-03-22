# scenes/settings_scene.py
import pygame
import math
import random
from settings import *

class SettingsScene:
    # noinspection PyPep8Naming
    def __init__(self, screen, W, H, previous_scene):
        self.screen          = screen
        self.W               = W
        self.H               = H
        self.previous_scene  = previous_scene  # scene to return to

        import settings as settings_module

        pygame.mixer.music.set_volume(settings_module.MUSIC_VOLUME * settings_module.MASTER_VOLUME)

        self.font_title = pygame.font.SysFont("couriernew", 60, bold=True)
        self.font_btn   = pygame.font.SysFont("couriernew", 26, bold=True)
        self.font_small = pygame.font.SysFont("couriernew", 16)

        self.tick      = 0
        self.particles = [self._new_particle() for _ in range(40)]

        btn_w, btn_h = 300, 55
        self.return_btn = pygame.Rect(self.W // 2 - btn_w // 2, self.H // 2 + 280, btn_w, btn_h)
        self.windowed_btn = pygame.Rect(self.W // 2 - btn_w // 2, self.H // 2 + 360, btn_w, btn_h)
        self.menu_btn = pygame.Rect(self.W // 2 - btn_w // 2, self.H // 2 + 440, btn_w, btn_h)
        self.exit_btn = pygame.Rect(self.W // 2 - btn_w // 2, self.H // 2 + 520, btn_w, btn_h)

        self.windowed_hovered = False
        self.menu_hovered     = False
        self.exit_hovered     = False
        self.request_windowed = False
        self.return_hovered = False

        # volume settings — load current values
        self.master_vol = MASTER_VOLUME
        self.music_vol = MUSIC_VOLUME
        self.sfx_vol = SFX_VOLUME

        # slider rects — track is the bar, handle is the draggable circle
        slider_x = self.W // 2 - 150
        slider_w = 300
        slider_h = 6
        handle_r = 12

        base_y = self.H // 2 - 260  # adjust this single value to move everything

        self.sliders = {
            "master": {
                "label": "MASTER",
                "vol": self.master_vol,
                "y": base_y,
                "dragging": False,
            },
            "music": {
                "label": "MUSIC",
                "vol": self.music_vol,
                "y": base_y + 80,
                "dragging": False,
            },
            "sfx": {
                "label": "SFX",
                "vol": self.sfx_vol,
                "y": base_y + 160,
                "dragging": False,
            },
        }
        self.slider_x = slider_x
        self.slider_w = slider_w
        self.slider_h = slider_h
        self.handle_r = handle_r

        btn_w, btn_h = 300, 55
        self.return_btn = pygame.Rect(self.W // 2 - btn_w // 2, base_y + 260, btn_w, btn_h)
        self.windowed_btn = pygame.Rect(self.W // 2 - btn_w // 2, base_y + 330, btn_w, btn_h)
        self.menu_btn = pygame.Rect(self.W // 2 - btn_w // 2, base_y + 400, btn_w, btn_h)
        self.exit_btn = pygame.Rect(self.W // 2 - btn_w // 2, base_y + 470, btn_w, btn_h)

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
        self.slider_x = self.W // 2 - 150
        base_y = self.H // 2 - 280
        btn_w, btn_h = 300, 55
        self.return_btn = pygame.Rect(self.W // 2 - btn_w // 2, base_y + 260, btn_w, btn_h)
        self.windowed_btn = pygame.Rect(self.W // 2 - btn_w // 2, base_y + 330, btn_w, btn_h)
        self.menu_btn = pygame.Rect(self.W // 2 - btn_w // 2, base_y + 400, btn_w, btn_h)
        self.exit_btn = pygame.Rect(self.W // 2 - btn_w // 2, base_y + 470, btn_w, btn_h)
        for key, s in self.sliders.items():
            s["y"] = {
                "master": base_y,
                "music": base_y + 80,
                "sfx": base_y + 160,
            }[key]

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.windowed_hovered = self.windowed_btn.collidepoint(event.pos)
            self.menu_hovered = self.menu_btn.collidepoint(event.pos)
            self.exit_hovered = self.exit_btn.collidepoint(event.pos)
            self.return_hovered = self.return_btn.collidepoint(event.pos)

            # drag sliders
            for key, s in self.sliders.items():
                if s["dragging"]:
                    raw = (event.pos[0] - self.slider_x) / self.slider_w
                    s["vol"] = max(0.0, min(1.0, raw))
                    self._apply_volumes()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # check slider handles
            for key, s in self.sliders.items():
                hx = self._handle_x(s["vol"])
                hy = s["y"] + self.slider_h // 2
                dx = event.pos[0] - hx
                dy = event.pos[1] - hy
                if dx * dx + dy * dy <= self.handle_r ** 2:
                    s["dragging"] = True
                    return None

            if self.return_btn.collidepoint(event.pos):
                return self.previous_scene
            if self.windowed_btn.collidepoint(event.pos):
                self.request_windowed = True
                return None
            if self.menu_btn.collidepoint(event.pos):
                from scenes.menu_scene import MenuScene
                return MenuScene(self.screen, self.W, self.H)
            if self.exit_btn.collidepoint(event.pos):
                import sys
                pygame.quit()
                sys.exit()

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for key, s in self.sliders.items():
                s["dragging"] = False

        return None

    def update(self, dt):
        self.tick += 1
        return None

    def draw(self):
        self.screen.fill((8, 10, 20))
        self._draw_particles()

        title = self.font_title.render("SETTINGS", True, (180, 180, 220))
        self.screen.blit(title, title.get_rect(
            centerx=self.W // 2, centery=self.H // 2 - 320))

        pygame.draw.line(self.screen, (50, 50, 80),
                         (self.W // 2 - 200, self.H // 2 - 270),
                         (self.W // 2 + 200, self.H // 2 - 270), 1)

        self._draw_sliders()

        self._draw_button(self.return_btn, "[ RETURN TO GAME ]",
                          self.return_hovered, (0, 220, 180), (0, 60, 55))
        self._draw_button(self.windowed_btn, "[ BORDERLESS WINDOW ]",
                          self.windowed_hovered, (0, 180, 220), (0, 50, 70))
        self._draw_button(self.menu_btn, "[ MAIN MENU ]",
                          self.menu_hovered, (220, 175, 50), (60, 45, 0))
        self._draw_button(self.exit_btn, "[ EXIT ]",
                          self.exit_hovered, (210, 50, 50), (60, 10, 10))

    def _handle_x(self, vol):
        return self.slider_x + int(vol * self.slider_w)

    def _draw_sliders(self):
        font_label = pygame.font.SysFont("couriernew", FONT_SIZE_SMALL, bold=True)
        font_val = pygame.font.SysFont("couriernew", FONT_SIZE_SMALL)

        for key, s in self.sliders.items():
            y = s["y"]
            vol = s["vol"]
            hx = self._handle_x(vol)

            # label
            label = font_label.render(s["label"], True, (180, 180, 220))
            self.screen.blit(label, (self.slider_x, y - 28))

            # value percentage
            val_surf = font_val.render(f"{int(vol * 100)}%", True, (120, 120, 160))
            self.screen.blit(val_surf, (self.slider_x + self.slider_w + 16, y - 5))

            # track background
            pygame.draw.rect(self.screen, (40, 40, 60),
                             (self.slider_x, y, self.slider_w, self.slider_h),
                             border_radius=3)

            # track fill
            pygame.draw.rect(self.screen, (0, 180, 220),
                             (self.slider_x, y, hx - self.slider_x, self.slider_h),
                             border_radius=3)

            # handle
            pygame.draw.circle(self.screen, (0, 220, 255), (hx, y + self.slider_h // 2), self.handle_r)
            pygame.draw.circle(self.screen, (180, 180, 220), (hx, y + self.slider_h // 2), self.handle_r, 2)

    def _apply_volumes(self):
        master = self.sliders["master"]["vol"]
        music = self.sliders["music"]["vol"]
        sfx = self.sliders["sfx"]["vol"]

        pygame.mixer.music.set_volume(music * master)

        # update settings module values so game scene can read them
        import settings
        settings.MASTER_VOLUME = master
        settings.MUSIC_VOLUME = music
        settings.SFX_VOLUME = sfx
