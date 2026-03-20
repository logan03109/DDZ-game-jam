# scenes/game_scene.py
from entities.player import Player, validate_set, Deck, damage_calc
from entities.npc1 import Boss
from settings import *
import pygame
# Card dimensions
CARD_W = 72
CARD_H = 100
CARD_GAP = 10

SUIT_SYMBOLS = {
    "Hearts": "♥", "Diamonds": "♦",
    "Spades": "♠", "Clubs": "♣", "Joker": "★"
}
SUIT_COLOURS = {
    "Hearts":   (210, 50,  50),
    "Diamonds": (210, 50,  50),
    "Spades":   (30,  30,  50),
    "Clubs":    (30,  30,  50),
    "Joker":    (220, 175, 50),
}

CARD_WHITE  = (240, 235, 220)
CARD_SHADOW = (10,  14,  30)
SELECTED_COL = (255, 220, 60)
BG_COLOUR   = (8,   12,  22)
PANEL_COL   = (20,  25,  45)
BORDER_COL  = (60,  70, 110)
WHITE       = (245, 245, 245)
GREY        = (120, 120, 135)
NEON_TEAL   = (0,   220, 180)
DARK_TEAL   = (0,    60,  55)
RED         = (210,  50,  50)
DARK_RED    = (80,   15,  15)
GOLD = (220, 175, 50)

class GameScene:
    def __init__(self, screen, W, H):
        self.screen = screen
        self.W = W
        self.H = H

        # Fonts
        self.font_card_val = pygame.font.SysFont("couriernew", FONT_SIZE_NORMAL, bold=True)
        self.font_card_sym = pygame.font.SysFont("segoeui", FONT_SIZE_NORMAL)
        self.font_ui = pygame.font.SysFont("couriernew", FONT_SIZE_UI, bold=True)
        self.font_msg = pygame.font.SysFont("couriernew", FONT_SIZE_MSG, bold=True)
        self.font_small = pygame.font.SysFont("couriernew", FONT_SIZE_SMALL)

        # Game state
        self.deck = Deck()
        self.deck.make_deck()

        self.selected = set()   # indices into self.player.hand.hand
        self.trigger_win = False
        self.trigger_lose = False
        self.message  = "Select cards and press PLAY"
        self.msg_col  = GREY
        self.msg_timer = 0      # how many frames to show message

        self.btn_radius = 60
        hand_top = self.H - CARD_H - 100

        btn_pad_right = 160  # distance from right edge
        btn_pad_bottom = 80  # bottom two buttons distance above hand
        btn_top_offset = 100  # how high the top button sits above the bottom two
        btn_spacing = 120  # horizontal distance between bottom two buttons

        self.sort_btn_center = (self.W - btn_pad_right - btn_spacing, hand_top - btn_pad_bottom)
        self.shuffle_btn_center = (self.W - btn_pad_right, hand_top - btn_pad_bottom)
        self.play_btn_center = (self.W - btn_pad_right - btn_spacing // 2, hand_top - btn_pad_bottom - btn_top_offset)

        self.play_hovered = False
        self.sort_hovered = False
        self.shuffle_hovered = False
        self.boss_index = 0
        self.boss = Boss(BOSS_CONFIGS[self.boss_index])
        self.allowed_sets = BOSS_CONFIGS[self.boss_index]["allowed_sets"]
        self.player_hand_size = BOSS_CONFIGS[self.boss_index]["hand_size"]
        self.player = Player(self.deck.deck, self.player_hand_size)
        self.player.hand.hand.sort(key=lambda card: card.numeric_rank())  # ADD
        self.plays_remaining = BOSS_CONFIGS[self.boss_index]["max_plays"]
        self.shuffles_remaining = BOSS_CONFIGS[self.boss_index]["max_shuffles"] + self.player.bonus_shuffles

        self.trigger_next_boss_scene = False

        self.card_rects = []


        self.hand_scroll = 0  # number of cards to skip from the left

        self.settings_btn = pygame.Rect(self.W - 120, 20, 115, 35)
        self.settings_hovered = False

        self.player_sprite = self._make_placeholder(80, 120, (40, 180, 80))  # green
        self.boss_sprite = self._make_placeholder(80, 120, (180, 40, 40))  # red
        # self.player_sprite = pygame.image.load("assets/images/sprites/player.png").convert_alpha()
        # self.boss_sprite = pygame.image.load("assets/images/sprites/boss.png").convert_alpha()

        self.show_tutorial = True  # shows on first load
        self.tutorial_ok_btn = pygame.Rect(self.W // 2 - 60, self.H // 2 + 180, 120, 45)
        self.tutorial_ok_hovered = False

        self.pending_next_boss = False
        self.pending_win = False
        self.next_boss_timer = 0
        self.NEXT_BOSS_DELAY = 90  # frames — roughly 1.5 seconds at 60fps
    # ── drawing helpers ───────────────────────────────────────

    def _draw_card(self, card, x, y, selected):
        """Draw a single card at (x, y), lifted if selected."""
        draw_y = y - 20 if selected else y

        # Shadow
        pygame.draw.rect(self.screen, CARD_SHADOW,
                         (x + 4, draw_y + 4, CARD_W, CARD_H), border_radius=10)

        # Face
        pygame.draw.rect(self.screen, CARD_WHITE,
                         (x, draw_y, CARD_W, CARD_H), border_radius=10)

        # Border — gold if selected, light grey otherwise
        border = SELECTED_COL if selected else (180, 180, 195)
        pygame.draw.rect(self.screen, border,
                         (x, draw_y, CARD_W, CARD_H), 3, border_radius=10)

        col = SUIT_COLOURS.get(card.suit, (30, 30, 50))
        sym = SUIT_SYMBOLS.get(card.suit, "?")

        if card.suit == "Joker":
            label1 = "BIG" if card.value == "Big" else "SML"
            label2 = "JKR"
            t1 = self.font_card_val.render(label1, True, col)
            t2 = self.font_card_val.render(label2, True, col)
            t3 = self.font_card_sym.render(sym, True, col)
            self.screen.blit(t1, t1.get_rect(centerx=x + CARD_W // 2, top=draw_y + 8))
            self.screen.blit(t2, t2.get_rect(centerx=x + CARD_W // 2, top=draw_y + 28))
            self.screen.blit(t3, t3.get_rect(centerx=x + CARD_W // 2, top=draw_y + 52))
        else:
            val_surf = self.font_card_val.render(card.value, True, col)
            sym_surf = self.font_card_sym.render(sym,        True, col)
            self.screen.blit(val_surf, (x + 6, draw_y + 5))
            self.screen.blit(sym_surf, (x + 6, draw_y + 24))

        # Return the rect for click detection (use un-lifted y for consistency)
        return pygame.Rect(x, y, CARD_W, CARD_H)

    def _draw_hand(self):
        hand = self.player.hand.hand

        # how many cards fit on screen
        max_visible = (self.W - 40) // (CARD_W + CARD_GAP)

        # clamp scroll so it never goes out of bounds
        self.hand_scroll = max(0, min(self.hand_scroll, len(hand) - max_visible))

        visible_hand = hand[self.hand_scroll:self.hand_scroll + max_visible]

        total_w = len(visible_hand) * (CARD_W + CARD_GAP) - CARD_GAP
        start_x = (self.W - total_w) // 2
        base_y = self.H - CARD_H - 100

        self.card_rects = []
        for i, card in enumerate(visible_hand):
            actual_index = i + self.hand_scroll  # real index in full hand
            x = start_x + i * (CARD_W + CARD_GAP)
            rect = self._draw_card(card, x, base_y, selected=(actual_index in self.selected))
            self.card_rects.append((actual_index, rect))  # store actual index with rect

        # draw scroll arrows if needed
        if self.hand_scroll > 0:
            self._draw_scroll_arrow(left=True)
        if self.hand_scroll + max_visible < len(hand):
            self._draw_scroll_arrow(left=False)

    def _draw_scroll_arrow(self, left):
        x = 10 if left else self.W - 40
        y = self.H - CARD_H - 60
        col = (0, 220, 180)
        txt = self.font_ui.render("<" if left else ">", True, col)
        self.screen.blit(txt, (x, y))

    def _draw_circle_button(self, center, label, hovered, border_col, hover_col):
        col = hover_col if hovered else (10, 15, 30)
        pygame.draw.circle(self.screen, col, center, self.btn_radius)
        pygame.draw.circle(self.screen, border_col, center, self.btn_radius, 2)
        txt = self.font_small.render(label, True, border_col if not hovered else (255, 255, 255))
        self.screen.blit(txt, txt.get_rect(center=center))

    def _draw_play_button(self):
        self._draw_circle_button(self.play_btn_center, "PLAY", self.play_hovered,
                                 NEON_TEAL, DARK_TEAL)

    def _draw_sort_button(self):
        self._draw_circle_button(self.sort_btn_center, "SORT", self.sort_hovered,
                                 (0, 120, 220), (10, 20, 45))

    def _draw_shuffle_button(self):
        self._draw_circle_button(self.shuffle_btn_center, "SHUFFLE", self.shuffle_hovered,
                                 (180, 0, 255), (25, 5, 35))

    def _sort_hand(self):
        self.player.hand.hand.sort(key=lambda card: card.numeric_rank())
        self.selected = set()  # clear selection since indices change after sort

    def _shuffle_hand(self):
        if self.shuffles_remaining <= 0:
            self.message = "No shuffles remaining!"
            self.msg_col = RED
            return

        for card in self.player.hand.hand:
            self.deck.pool.append(card)
        self.player.hand.hand = []

        self.deck.redeck()

        for _ in range(self.player.hand_size):
            if self.deck.deck:
                self.player.hand.hand.append(self.deck.deck.pop())
            else:
                break

        self.shuffles_remaining -= 1  # ADD
        self.selected = set()
        self.message = f"Hand reshuffled!  |  {self.shuffles_remaining} shuffles left"
        self.msg_col = (200, 80, 255)

    def _draw_message(self):
        if self.message:
            # split into two lines if too long
            parts = self.message.split("  |  ")
            if len(parts) == 2:
                line1 = parts[0]
                line2 = f"| {parts[1]}"
            else:
                line1 = self.message
                line2 = None

            txt1 = self.font_msg.render(line1, True, self.msg_col)
            self.screen.blit(txt1, txt1.get_rect(
                centerx=self.W // 2, centery=self.H - CARD_H - 180))

            if line2:
                txt2 = self.font_msg.render(line2, True, self.msg_col)
                self.screen.blit(txt2, txt2.get_rect(
                    centerx=self.W // 2, centery=self.H - CARD_H - 140))

    def _draw_info(self):
        # Card counter — top left
        pygame.draw.rect(self.screen, PANEL_COL, (20, 20, 200, 50), border_radius=8)
        pygame.draw.rect(self.screen, BORDER_COL, (20, 20, 200, 50), 1, border_radius=8)
        card_count = self.font_small.render(
            f"CARDS LEFT: {len(self.deck.deck) + len(self.player.hand.hand)}", True, WHITE)
        self.screen.blit(card_count, card_count.get_rect(center=(120, 45)))

        # Active gimmicks panel
        gimmick_panel_h = max(50, 20 + len(self.player.active_gimmicks) * 18)
        pygame.draw.rect(self.screen, PANEL_COL, (20, 80, 200, gimmick_panel_h), border_radius=8)
        pygame.draw.rect(self.screen, BORDER_COL, (20, 80, 200, gimmick_panel_h), 1, border_radius=8)

        title_surf = self.font_small.render("MODIFIERS", True, GOLD)
        self.screen.blit(title_surf, title_surf.get_rect(centerx=120, top=86))

        if not self.player.active_gimmicks:
            none_surf = self.font_small.render("none", True, GREY)
            self.screen.blit(none_surf, none_surf.get_rect(centerx=120, top=104))
        else:
            for i, g in enumerate(self.player.active_gimmicks):
                label = g.upper().replace("_", " ")
                g_surf = self.font_small.render(f"+ {label}", True, NEON_TEAL)
                self.screen.blit(g_surf, g_surf.get_rect(topleft=(30, 104 + i * 18)))

        # Boss health bar — top centre
        bar_w, bar_h = 400, 30
        bar_x = self.W // 2 - bar_w // 2
        bar_y = 20

        # Background
        pygame.draw.rect(self.screen, (40, 10, 10), (bar_x, bar_y, bar_w, bar_h), border_radius=8)

        # Fill — clamped so it never goes below 0
        fill = max(0, int(bar_w * (self.boss.hp / self.boss.max_hp)))
        if fill > 0:
            pygame.draw.rect(self.screen, (200, 40, 40), (bar_x, bar_y, fill, bar_h), border_radius=8)

        # Border                                                          # ADD FROM HERE
        pygame.draw.rect(self.screen, (220, 60, 60), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=8)

        # Boss name inside bar
        boss_label = self.font_small.render(f"{self.boss.name}", True, WHITE)
        self.screen.blit(boss_label, boss_label.get_rect(center=(self.W // 2, bar_y + bar_h // 2)))

        # HP number below bar
        hp_label = self.font_small.render(f"{max(0, self.boss.hp)}", True, (220, 60, 60))
        self.screen.blit(hp_label, hp_label.get_rect(center=(self.W // 2, bar_y + bar_h + 15)))

        plays_surf = self.font_small.render(f"PLAYS LEFT: {self.plays_remaining}", True, NEON_TEAL)
        self.screen.blit(plays_surf, plays_surf.get_rect(topleft=(20, 80 + gimmick_panel_h + 10)))

        shuffles_surf = self.font_small.render(f"SHUFFLES LEFT: {self.shuffles_remaining}", True, (200, 80, 255))
        self.screen.blit(shuffles_surf, shuffles_surf.get_rect(topleft=(20, 80 + gimmick_panel_h + 28)))

    def _next_boss(self):
        self.boss_index += 1
        if self.boss_index >= len(BOSS_CONFIGS):
            self.pending_win = True
            self.next_boss_timer = self.NEXT_BOSS_DELAY
        else:
            # just set the timer — don't load next boss yet
            self.pending_next_boss = True
            self.next_boss_timer = self.NEXT_BOSS_DELAY

    def _load_next_boss(self):
        config = BOSS_CONFIGS[self.boss_index]
        self.boss = Boss(config)
        self.allowed_sets = config["allowed_sets"]
        self.player_hand_size = config["hand_size"]
        self.player.hand_size = config["hand_size"]
        self.plays_remaining = config["max_plays"]
        self.shuffles_remaining = config["max_shuffles"] + self.player.bonus_shuffles

        self.deck = Deck()
        self.deck.make_deck()

        self.player.hand.hand = []
        for _ in range(self.player.hand_size):
            if self.deck.deck:
                self.player.hand.hand.append(self.deck.deck.pop())

        self.player.hand.hand.sort(key=lambda card: card.numeric_rank())
        self.selected = set()
        self.show_tutorial = True

    def _draw_sprites(self):
        hand_top = self.H - CARD_H - 100

        # Player sprite — bottom left
        player_pad_left = 500
        player_pad_bottom = 200
        sprite_x = player_pad_left
        sprite_y = hand_top - self.player_sprite.get_height() - player_pad_bottom
        self.screen.blit(self.player_sprite, (sprite_x, sprite_y))

        # Boss sprite — top right
        boss_pad_right = 500
        boss_pad_top = 200
        boss_sprite_x = self.W - self.boss_sprite.get_width() - boss_pad_right
        boss_sprite_y = boss_pad_top
        self.screen.blit(self.boss_sprite, (boss_sprite_x, boss_sprite_y))

    def on_resize(self, W, H):
        self.W = W
        self.H = H

        hand_top = self.H - CARD_H - 100

        btn_pad_right = 160  # distance from right edge
        btn_pad_bottom = 80  # bottom two buttons distance above hand
        btn_top_offset = 100  # how high the top button sits above the bottom two
        btn_spacing = 120  # horizontal distance between bottom two buttons

        # bottom left of triangle
        self.sort_btn_center = (self.W - btn_pad_right - btn_spacing, hand_top - btn_pad_bottom)
        # bottom right of triangle
        self.shuffle_btn_center = (self.W - btn_pad_right, hand_top - btn_pad_bottom)
        # top centre of triangle
        self.play_btn_center = (self.W - btn_pad_right - btn_spacing // 2, hand_top - btn_pad_bottom - btn_top_offset)

        self.tutorial_ok_btn = pygame.Rect(self.W // 2 - 60, self.H // 2 + 180, 120, 45)

    def _make_placeholder(self, w, h, colour):
        """Replace this with pygame.image.load('path/to/sprite.png') when art is ready."""
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill(colour)
        return surf
    # ── game logic ────────────────────────────────────────────

    def _play_turn(self):
        if not self.selected:
            self.message = "No cards selected!"
            self.msg_col = RED
            return

        cards = [self.player.hand.hand[i] for i in sorted(self.selected)]
        valid, ddz_set, cards = validate_set(cards)

        if not valid:
            self.message = "INVALID SET"
            self.msg_col = RED
            return

        if ddz_set not in self.allowed_sets:
            self.message = f"{ddz_set.upper()} is not allowed!"
            self.msg_col = RED
            return

        has_gambling = "damage_multiplier" in self.player.active_gimmicks
        dmg, roll = damage_calc(cards, ddz_set, self.player.damage_mult, has_gambling)
        self.boss.hp -= int(dmg)

        highest = max(card.numeric_rank() for card in cards)
        base = base_damage_constant[ddz_set]
        mult = self.player.damage_mult

        if roll is not None:
            calc_str = f"{highest} x {base} x {round(roll, 1)} = {int(dmg)}"
        elif mult != 1:
            calc_str = f"{highest} x {base} x {round(mult, 2)} = {int(dmg)}"
        else:
            calc_str = f"{highest} x {base} = {int(dmg)}"

        self.message = f"{ddz_set.upper()}!  {calc_str}  |  {self.plays_remaining - 1} plays left"
        self.msg_col = NEON_TEAL
        for card in cards:
            self.player.hand.hand.remove(card)
        # refill hand up to current hand size
        cards_to_draw = self.player.hand_size - len(self.player.hand.hand)
        for _ in range(min(cards_to_draw, len(self.deck.deck))):
            self.player.hand.hand.append(self.deck.deck.pop())

        self.player.hand.hand.sort(key=lambda card: card.numeric_rank())

        if self.plays_remaining == 1 and self.boss.hp > 0:
            self.trigger_lose = True

        self.plays_remaining -= 1
        self.selected = set()

        if self.boss.hp <= 0:
            self._next_boss()

    def _draw_settings_button(self):
        col = (20, 20, 40) if self.settings_hovered else (10, 10, 20)
        pygame.draw.rect(self.screen, col, self.settings_btn, border_radius=8)
        pygame.draw.rect(self.screen, (100, 100, 160), self.settings_btn, 2, border_radius=8)
        label_col = (180, 180, 220) if self.settings_hovered else (120, 120, 160)
        txt = self.font_small.render("SETTINGS", True, label_col)
        self.screen.blit(txt, txt.get_rect(center=self.settings_btn.center))

    def _draw_tutorial(self):
        if not self.show_tutorial:
            return

        # dim the background
        overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))


        # tutorial text
        lines = [
            f"You have {self.plays_remaining} plays this fight.",
            f"You have {self.shuffles_remaining} shuffles this fight.",
            f"Each shuffle redraws your entire hand.",
            "",
            "Select cards from your hand and press",
            "PLAY to deal damage to the boss.",
            "",
            "Allowed sets this fight:",
            *[f"  - {s}" for s in self.allowed_sets],
            "",
            "Defeat the boss before your plays run out!",
        ]

        # Re-sizes the HOW TO PLAY box to fit the text
        max_width = 0
        for line in lines:
            line_w, line_h = self.font_small.size(line)
            if line_w > max_width:
                max_width = line_w

        box_w = max_width + 60

        box_h = 70 + (len(lines) * 22) + 80

        box_x = (self.W - box_w) // 2
        box_y = (self.H - box_h) // 2

        self.tutorial_ok_btn = pygame.Rect(self.W // 2 - 50, box_y + box_h - 60, 100, 40)

        pygame.draw.rect(self.screen, (20, 20, 25), (box_x,box_y, box_w, box_h), border_radius=12)
        pygame.draw.rect(self.screen, (0, 220, 180), (box_x, box_y, box_w, box_h), 2, border_radius=12)

        # title
        title = self.font_ui.render("HOW TO PLAY", True, (0, 220, 180))
        self.screen.blit(title, title.get_rect(centerx=self.W // 2, top=box_y + 20))
        # divider
        pygame.draw.line(self.screen, (0, 220, 180),
                         (box_x + 20, box_y + 55),
                         (box_x + box_w - 20, box_y + 55), 1)

        for i, line in enumerate(lines):
            col = (180, 180, 200) if not line.startswith("  -") else (0, 180, 140)
            surf = self.font_small.render(line, True, col)
            self.screen.blit(surf, (box_x + 30, box_y + 70 + i * 22))

        # ok button
        ok_col = (0, 60, 55) if self.tutorial_ok_hovered else (10, 30, 28)
        pygame.draw.rect(self.screen, ok_col, self.tutorial_ok_btn, border_radius=8)
        pygame.draw.rect(self.screen, (0, 220, 180), self.tutorial_ok_btn, 2, border_radius=8)
        ok_label = self.font_small.render("[ OK ]", True, (0, 220, 180))
        self.screen.blit(ok_label, ok_label.get_rect(center=self.tutorial_ok_btn.center))
    # ── scene interface ───────────────────────────────────────

    def _point_in_circle(self, point, center):
        dx = point[0] - center[0]
        dy = point[1] - center[1]
        return (dx * dx + dy * dy) <= self.btn_radius ** 2

    def handle_event(self, event):
        if self.show_tutorial:
            if event.type == pygame.MOUSEMOTION:
                self.tutorial_ok_hovered = self.tutorial_ok_btn.collidepoint(event.pos)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.tutorial_ok_btn.collidepoint(event.pos):
                    self.show_tutorial = False
            return None
        if event.type == pygame.MOUSEMOTION:
            self.play_hovered = self._point_in_circle(event.pos, self.play_btn_center)
            self.sort_hovered = self._point_in_circle(event.pos, self.sort_btn_center)
            self.shuffle_hovered = self._point_in_circle(event.pos, self.shuffle_btn_center)
            self.settings_hovered = self.settings_btn.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.settings_btn.collidepoint(event.pos):
                from scenes.settings_scene import SettingsScene
                return SettingsScene(self.screen, self.W, self.H, self)
            if self._point_in_circle(event.pos, self.play_btn_center):
                self._play_turn()
                return None
            if self._point_in_circle(event.pos, self.sort_btn_center):
                self._sort_hand()
                return None
            if self._point_in_circle(event.pos, self.shuffle_btn_center):
                self._shuffle_hand()
                return None

            arrow_y = self.H - CARD_H - 60
            left_arrow = pygame.Rect(10, arrow_y, 30, 40)
            right_arrow = pygame.Rect(self.W - 40, arrow_y, 30, 40)
            if left_arrow.collidepoint(event.pos):
                self.hand_scroll -= 1
                return None
            if right_arrow.collidepoint(event.pos):
                self.hand_scroll += 1
                return None

            for actual_index, rect in self.card_rects:
                if rect.collidepoint(event.pos):
                    if actual_index in self.selected:
                        self.selected.discard(actual_index)
                    else:
                        self.selected.add(actual_index)
                    return None

        if event.type == pygame.MOUSEWHEEL:
            self.hand_scroll -= event.y
            return None

        return None

    def update(self, dt):
        if self.next_boss_timer > 0:
            self.next_boss_timer -= 1
            return None

        if self.pending_win:
            from scenes.win_scene import WinScene
            return WinScene(self.screen, self.W, self.H)
        if self.trigger_lose:
            from scenes.lose_scene import LoseScene
            return LoseScene(self.screen, self.W, self.H)
        if self.pending_next_boss:
            self.pending_next_boss = False
            self._load_next_boss()
            from scenes.next_boss_scene import NextBossScene
            return NextBossScene(self.screen, self.W, self.H, self.boss_index, self)
        return None

    def draw(self):
        self.screen.fill(BG_COLOUR)
        self._draw_info()
        self._draw_hand()
        self._draw_message()
        self._draw_play_button()
        self._draw_sort_button()
        self._draw_shuffle_button()
        self._draw_settings_button()
        self._draw_sprites()
        self._draw_tutorial()