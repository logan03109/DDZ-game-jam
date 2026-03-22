# scenes/next_boss_scene.py
import pygame
import math
import random
from settings import BOSS_CONFIGS, GIMMICK_DESCRIPTIONS, gimmicks, GIMMICK_CARD_CONFIGS

class NextBossScene:
    def __init__(self, screen, W, H, boss_index, game_state):
        self.screen     = screen
        self.W          = W
        self.H          = H
        self.boss_index = boss_index
        self.game_state = game_state

        import settings as settings_module

        pygame.mixer.music.set_volume(settings_module.MUSIC_VOLUME * settings_module.MASTER_VOLUME)

        self.font_title   = pygame.font.SysFont("couriernew", 50, bold=True)
        self.font_sub     = pygame.font.SysFont("couriernew", 20)
        self.font_btn     = pygame.font.SysFont("couriernew", 24, bold=True)
        self.font_small   = pygame.font.SysFont("couriernew", 16)
        self.font_gimmick = pygame.font.SysFont("couriernew", 18, bold=True)

        self.tick           = 0
        self.particles      = [self._new_particle() for _ in range(60)]
        self.selected_gimmick = None   # which gimmick the player picked

        # gimmick button rects — 4 options laid out in a row
        g_btn_w, g_btn_h = 240, 80
        total_w = len(gimmicks) * g_btn_w + (len(gimmicks) - 1) * 20
        start_x = self.W // 2 - total_w // 2
        self.gimmick_btns = []
        for i, g in enumerate(gimmicks):
            rect = pygame.Rect(start_x + i * (g_btn_w + 20),
                               self.H // 2 + 20, g_btn_w, g_btn_h)
            self.gimmick_btns.append((g, rect))
        self.gimmick_hovered = None

        # play button — only active after gimmick selected
        btn_w, btn_h = 220, 55
        self.play_btn = pygame.Rect(self.W // 2 - btn_w // 2,
                                    self.H // 2 + 230, btn_w, btn_h)
        self.play_hovered = False

        self.selected_gimmick_card = None
        self.gimmick_card_hovered = None

        gc_btn_w, gc_btn_h = 240, 80
        gc_total_w = len(GIMMICK_CARD_CONFIGS) * gc_btn_w + (len(GIMMICK_CARD_CONFIGS) - 1) * 20
        gc_start_x = self.W // 2 - gc_total_w // 2
        self.gimmick_card_btns = []
        for i, (val, cfg) in enumerate(GIMMICK_CARD_CONFIGS.items()):
            rect = pygame.Rect(gc_start_x + i * (gc_btn_w + 20),
                               self.H // 2 + 120, gc_btn_w, gc_btn_h)
            self.gimmick_card_btns.append((val, cfg, rect))

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
            ...

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for g, rect in self.gimmick_btns:
                if rect.collidepoint(event.pos):
                    if g not in self.game_state.player.active_gimmicks:
                        self.selected_gimmick = g
                    return None
            for val, cfg, rect in self.gimmick_card_btns:
                if rect.collidepoint(event.pos):
                    self.selected_gimmick_card = val
                    return None
            if self.play_btn.collidepoint(event.pos) and self.selected_gimmick:
                self.game_state.player.apply_gimmick(self.selected_gimmick, self.game_state.deck)
                if self.selected_gimmick_card:
                    if self.selected_gimmick_card not in self.game_state.player.gimmick_card:
                        self.game_state.player.gimmick_card.append(self.selected_gimmick_card)
                return self.game_state

        return None  # ADD THIS

    def update(self, dt):
        self.tick += 1
        return None

    def draw(self):
        self.screen.fill((8, 12, 22))
        self._draw_particles()

        boss = BOSS_CONFIGS[self.boss_index]

        # UP NEXT
        up_next = self.font_small.render("-- UP NEXT --", True, (100, 100, 120))
        self.screen.blit(up_next, up_next.get_rect(
            centerx=self.W // 2, centery=self.H // 2 - 160))

        # Boss name
        pulse    = abs(math.sin(self.tick * 0.04))
        name_col = (int(200 + pulse * 55), int(40 + pulse * 20), int(40 + pulse * 20))
        name_surf = self.font_title.render(boss["name"], True, name_col)
        self.screen.blit(name_surf, name_surf.get_rect(
            centerx=self.W // 2, centery=self.H // 2 - 110))

        # Choose gimmick label
        choose = self.font_sub.render("Choose a gimmick for the next fight:", True, (180, 180, 200))
        self.screen.blit(choose, choose.get_rect(
            centerx=self.W // 2, centery=self.H // 2 - 30))

        # Gimmick buttons
        for g, rect in self.gimmick_btns:
            is_selected = self.selected_gimmick == g
            is_hovered = self.gimmick_hovered == g
            already_owned = g in self.game_state.player.active_gimmicks  # use g, not val

            if is_selected:
                bg_col     = (0, 60, 55)
                border_col = (0, 220, 180)
            elif is_hovered:
                bg_col     = (30, 20, 50)
                border_col = (160, 80, 255)
            else:
                bg_col     = (15, 10, 25)
                border_col = (60, 40, 90)

            pygame.draw.rect(self.screen, bg_col,     rect, border_radius=8)
            pygame.draw.rect(self.screen, border_col, rect, 2, border_radius=8)

            name_col = (50, 50, 50) if already_owned else border_col
            name_s = self.font_gimmick.render(g.upper().replace("_", " "), True, border_col)
            self.screen.blit(name_s, name_s.get_rect(
                centerx=rect.centerx, centery=rect.top + 25))

            desc_col = (60, 60, 60) if already_owned else (160, 160, 180)
            desc_s = self.font_small.render(GIMMICK_DESCRIPTIONS[g], True, (160, 160, 180))
            desc_s = pygame.transform.scale(desc_s, (rect.w - 10, desc_s.get_height()))
            self.screen.blit(desc_s, desc_s.get_rect(
                centerx=rect.centerx, centery=rect.top + 55))

            if already_owned:  # ADD owned label
                owned_s = self.font_small.render("OWNED", True, (80, 80, 80))
                self.screen.blit(owned_s, owned_s.get_rect(
                    centerx=rect.centerx, centery=rect.top + 65))

        # Play button — greyed out until gimmick chosen
        if self.selected_gimmick:
            border_col = (0, 220, 180)
            label_col  = (0, 220, 180) if self.play_hovered else (160, 210, 200)
            bg_col     = (0, 60, 55)   if self.play_hovered else (10, 30, 28)
        else:
            border_col = (60, 60, 60)
            label_col  = (80, 80, 80)
            bg_col     = (15, 15, 15)

        pygame.draw.rect(self.screen, bg_col,     self.play_btn, border_radius=8)
        pygame.draw.rect(self.screen, border_col, self.play_btn, 2, border_radius=8)
        txt = self.font_btn.render("[ PLAY ]", True, label_col)
        self.screen.blit(txt, txt.get_rect(center=self.play_btn.center))

        # Gimmick card section label
        gc_label = self.font_sub.render("Choose a gimmick card:", True, (180, 180, 200))
        self.screen.blit(gc_label, gc_label.get_rect(
            centerx=self.W // 2, centery=self.H // 2 + 100))

        # Gimmick card buttons
        for val, cfg, rect in self.gimmick_card_btns:
            is_selected = self.selected_gimmick_card == val
            is_hovered = self.gimmick_card_hovered == val
            already_owned = val in self.game_state.player.gimmick_card

            if already_owned:
                bg_col = (20, 20, 20)
                border_col = (50, 50, 50)
            elif is_selected:
                bg_col = (50, 40, 0)
                border_col = (220, 175, 50)
            elif is_hovered:
                bg_col = (40, 30, 10)
                border_col = (180, 140, 40)
            else:
                bg_col = (15, 12, 5)
                border_col = (80, 65, 20)

            pygame.draw.rect(self.screen, bg_col, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_col, rect, 2, border_radius=8)

            name_s = self.font_gimmick.render(f"CARD: {val}", True, border_col)
            self.screen.blit(name_s, name_s.get_rect(
                centerx=rect.centerx, centery=rect.top + 25))

            desc_s = self.font_small.render(cfg["description"], True, (160, 160, 180))
            desc_s = pygame.transform.scale(desc_s, (rect.w - 10, desc_s.get_height()))
            self.screen.blit(desc_s, desc_s.get_rect(
                centerx=rect.centerx, centery=rect.top + 55))

            if already_owned:
                owned_s = self.font_small.render("ACTIVE", True, (80, 80, 80))
                self.screen.blit(owned_s, owned_s.get_rect(
                    centerx=rect.centerx, centery=rect.top + 65))

    def on_resize(self, W, H):
        self.W = W
        self.H = H
        g_btn_w, g_btn_h = 240, 80
        total_w = len(gimmicks) * g_btn_w + (len(gimmicks) - 1) * 20
        start_x = self.W // 2 - total_w // 2
        self.gimmick_btns = []
        for i, g in enumerate(gimmicks):
            rect = pygame.Rect(start_x + i * (g_btn_w + 20),
                               self.H // 2 + 20, g_btn_w, g_btn_h)
            self.gimmick_btns.append((g, rect))
        btn_w, btn_h = 220, 55
        self.play_btn = pygame.Rect(self.W // 2 - btn_w // 2,
                                    self.H // 2 + 140, btn_w, btn_h)

        gc_btn_w, gc_btn_h = 240, 80
        gc_total_w = len(GIMMICK_CARD_CONFIGS) * gc_btn_w + (len(GIMMICK_CARD_CONFIGS) - 1) * 20
        gc_start_x = self.W // 2 - gc_total_w // 2
        self.gimmick_card_btns = []
        for i, (val, cfg) in enumerate(GIMMICK_CARD_CONFIGS.items()):
            rect = pygame.Rect(gc_start_x + i * (gc_btn_w + 20),
                               self.H // 2 + 120, gc_btn_w, gc_btn_h)
            self.gimmick_card_btns.append((val, cfg, rect))
        btn_w, btn_h = 220, 55
        self.play_btn = pygame.Rect(self.W // 2 - btn_w // 2,
                                    self.H // 2 + 230, btn_w, btn_h)
