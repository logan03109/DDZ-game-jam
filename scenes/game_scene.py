# scenes/game_scene.py
from entities.player import Player, validate_set, Deck, damage_calc
from entities.npc1 import Boss
from settings import *
import pygame
import random
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
    def __init__(self, screen, W, H, existing_player=None):
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
        self.player.hand.hand.sort(key=lambda card: card.numeric_rank())
        self.plays_remaining = BOSS_CONFIGS[self.boss_index]["max_plays"]
        self.shuffles_remaining = BOSS_CONFIGS[self.boss_index]["max_shuffles"] + self.player.bonus_shuffles

        self.card_rects = []


        self.hand_scroll = 0  # number of cards to skip from the left

        self.settings_btn = pygame.Rect(self.W - 120, 20, 115, 35)
        self.settings_hovered = False

        self.boss_sprite = self._load_boss_sprite()

        self.show_tutorial = True  # shows on first load
        self.tutorial_ok_btn = pygame.Rect(self.W // 2 - 60, self.H // 2 + 180, 120, 45)
        self.tutorial_ok_hovered = False

        self.pending_next_boss = False
        self.pending_win = False
        self.next_boss_timer = 0
        self.NEXT_BOSS_DELAY = 90  # frames — roughly 1.5 seconds at 60fps

        pygame.mixer.init()
        self.sound_card_pickup = pygame.mixer.Sound(resource_path("assets/audio/sfx/pick up.wav"))
        self.sound_invalid = pygame.mixer.Sound(resource_path("assets/audio/sfx/invalid set.wav"))

        self.sound_attack_small = pygame.mixer.Sound(resource_path("assets/audio/sfx/small.wav"))
        self.sound_attack_big = pygame.mixer.Sound(resource_path("assets/audio/sfx/large.wav"))
        self.sound_attack_small.set_volume(0.5)
        self.sound_attack_big.set_volume(0.5)

        # Music
        pygame.mixer.music.load(resource_path("assets/audio/music/GDLTDDZ unfinished.wav"))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        self.anim_card_positions = []  # current x,y positions of animating cards
        self.anim_card_targets = []  # target x,y positions
        self.ANIM_CARD_SPEED = 0.15  # interpolation speed 0-1, higher = faster

        # Animation state
        self.anim_phase = 0  # 0 = idle, 1 = show cards, 2 = show damage, 3 = animate hp
        self.anim_timer = 0
        self.anim_cards = []  # cards being displayed during animation
        self.anim_ddz_set = None
        self.anim_dmg = 0
        self.anim_roll = None
        self.anim_boss_hp_display = 0  # the HP shown on the bar during animation
        self.ANIM_SHOW_CARDS = 40  # frames to show played cards
        self.ANIM_SHOW_DAMAGE = 20  # frames to show damage calculation
        self.ANIM_HP_SPEED = 1  # hp drained per frame during animation

        # Background image
        self.bg_image = self._load_bg()

        self.debug_mode = False
        self.debug_event = ""
        self.debug_event_timer = 0

        if existing_player:
            self.player = existing_player
            self.player.hand.hand = []
            self.player.hand_size = self.player_hand_size  # reset to boss 1 hand size
            for _ in range(self.player_hand_size):
                if self.deck.deck:
                    self.player.hand.hand.append(self.deck.deck.pop())
            self.player.hand.hand.sort(key=lambda card: card.numeric_rank())
            # active_gimmicks, gimmick_card, damage_mult, bonus_shuffles all preserved
        else:
            self.player = Player(self.deck.deck, self.player_hand_size)
            self.player.hand.hand.sort(key=lambda card: card.numeric_rank())

        try:
            self.img_play = pygame.image.load(resource_path("assets/images/ui/play_btn.png")).convert_alpha()
            self.img_sort = pygame.image.load(resource_path("assets/images/ui/sort_btn.png")).convert_alpha()
            self.img_shuffle = pygame.image.load(resource_path("assets/images/ui/shuffle_btn.png")).convert_alpha()
        except:
            self.img_play = None
            self.img_sort = None
            self.img_shuffle = None
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

    def _draw_circle_button(self, center, label, hovered, border_col, hover_col, img=None):
        if img:
            # scale image to button diameter
            size = self.btn_radius * 2
            scaled = pygame.transform.scale(img, (size, size))
            if hovered:
                scaled.set_alpha(200)
            else:
                scaled.set_alpha(255)
            rect = scaled.get_rect(center=center)
            self.screen.blit(scaled, rect)
            # border ring
            pygame.draw.circle(self.screen, border_col, center, self.btn_radius, 2)
        else:
            col = hover_col if hovered else (10, 15, 30)
            pygame.draw.circle(self.screen, col, center, self.btn_radius)
            pygame.draw.circle(self.screen, border_col, center, self.btn_radius, 2)
            txt = self.font_small.render(label, True, border_col if not hovered else (255, 255, 255))
            self.screen.blit(txt, txt.get_rect(center=center))

    def _draw_play_button(self):
        self._draw_circle_button(self.play_btn_center, "PLAY", self.play_hovered,
                                 NEON_TEAL, DARK_TEAL, self.img_play)

    def _draw_sort_button(self):
        self._draw_circle_button(self.sort_btn_center, "SORT", self.sort_hovered,
                                 (0, 120, 220), (10, 20, 45), self.img_sort)

    def _draw_shuffle_button(self):
        self._draw_circle_button(self.shuffle_btn_center, "SHUFFLE", self.shuffle_hovered,
                                 (180, 0, 255), (25, 5, 35), self.img_shuffle)

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

        pygame.draw.rect(self.screen, (40, 10, 10), (bar_x, bar_y, bar_w, bar_h), border_radius=8)
        pygame.draw.rect(self.screen, (220, 60, 60), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=8)

        display_hp = self.anim_boss_hp_display if self.anim_phase != 0 else self.boss.hp
        fill = max(0, int(bar_w * (display_hp / self.boss.max_hp)))
        if fill > 0:
            pygame.draw.rect(self.screen, (200, 40, 40), (bar_x, bar_y, fill, bar_h), border_radius=8)

        boss_label = self.font_small.render(f"{self.boss.name}", True, WHITE)
        self.screen.blit(boss_label, boss_label.get_rect(
            center=(self.W // 2, bar_y + bar_h // 2)))

        hp_label = self.font_small.render(f"{max(0, int(display_hp))}", True, (220, 60, 60))
        self.screen.blit(hp_label, hp_label.get_rect(
            center=(self.W // 2, bar_y + bar_h + 15)))

        # Boss stats
        stats_str = ""
        if self.boss.damage_reduction > 0:
            stats_str += f"DMG REDUCTION: {int(self.boss.damage_reduction * 100)}%  "
        if self.boss.regen > 0:
            stats_str += f"REGEN: +{self.boss.regen}/turn"
        if stats_str:
            stats_surf = self.font_small.render(stats_str, True, (180, 120, 120))
            self.screen.blit(stats_surf, stats_surf.get_rect(
                centerx=self.W // 2, top=bar_y + bar_h + 30))

        plays_surf = self.font_small.render(f"PLAYS LEFT: {self.plays_remaining}", True, NEON_TEAL)
        self.screen.blit(plays_surf, plays_surf.get_rect(topleft=(20, 80 + gimmick_panel_h + 10)))

        shuffles_surf = self.font_small.render(f"SHUFFLES LEFT: {self.shuffles_remaining}", True, (200, 80, 255))
        self.screen.blit(shuffles_surf, shuffles_surf.get_rect(topleft=(20, 80 + gimmick_panel_h + 28)))

    def _load_bg(self):
        config = BOSS_CONFIGS[self.boss_index]
        try:
            img = pygame.image.load(resource_path(config["background"])).convert()
            return pygame.transform.scale(img, (self.W, self.H))
        except:
            surf = pygame.Surface((self.W, self.H))
            surf.fill(BG_COLOUR)
            return surf

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
        self.bg_image = self._load_bg()

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

    def on_resize(self, W, H):
        self.W = W
        self.H = H
        self.bg_image = pygame.transform.scale(self.bg_image, (self.W, self.H))
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
        if self.anim_phase != 0:
            return

        # bleed tick
        if self.boss.bleed_stacks > 0:
            bleed_dmg = self.boss.bleed_stacks * 10
            self.boss.hp -= bleed_dmg
            self.debug_event = f"BLEED TICK -{bleed_dmg} ({self.boss.bleed_stacks} stacks)"
            self.debug_event_timer = 120

        # boss regen
        if self.boss.regen > 0:
            self.boss.hp = min(self.boss.max_hp, self.boss.hp + self.boss.regen)
            self.debug_event = f"BOSS REGEN +{self.boss.regen}"
            self.debug_event_timer = 120

        if not self.selected:
            self.message = "No cards selected!"
            self.msg_col = RED
            return

        cards = [self.player.hand.hand[i] for i in sorted(self.selected)]
        valid, ddz_set, cards = validate_set(cards)

        if not valid:
            self.message = "INVALID SET"
            self.msg_col = RED
            self.sound_invalid.play()
            return

        if ddz_set not in self.allowed_sets:
            self.message = f"{ddz_set.upper()} is not allowed!"
            self.msg_col = RED
            self.sound_invalid.play()
            return

        has_gambling = "damage_multiplier" in self.player.active_gimmicks
        dmg, roll = damage_calc(cards, ddz_set, self.player.damage_mult, has_gambling)

        if ddz_set in ("single", "double"):
            self.sound_attack_small.play()
        else:
            self.sound_attack_big.play()

        # store animation state BEFORE applying damage
        self.anim_cards = cards
        self.anim_ddz_set = ddz_set
        self.anim_dmg = int(dmg)
        self.anim_roll = roll
        self.anim_boss_hp_display = self.boss.hp
        self.anim_phase = 1
        self.anim_timer = self.ANIM_SHOW_CARDS

        # capture starting positions
        total_w = len(self.anim_cards) * (CARD_W + CARD_GAP) - CARD_GAP
        start_tx = (self.W - total_w) // 2
        target_y = self.H // 2 - CARD_H // 2

        self.anim_card_positions = []
        self.anim_card_targets = []

        for i, card in enumerate(self.anim_cards):
            start_x = self.W // 2
            start_y = self.H - CARD_H - 100
            for actual_index, rect in self.card_rects:
                if actual_index < len(self.player.hand.hand) and self.player.hand.hand[actual_index] == card:
                    start_x = rect.x
                    start_y = rect.y
                    break
            self.anim_card_positions.append([float(start_x), float(start_y)])
            self.anim_card_targets.append([float(start_tx + i * (CARD_W + CARD_GAP)), float(target_y)])

        # apply boss damage reduction
        actual_dmg = int(self.anim_dmg * (1 - self.boss.damage_reduction))
        self.boss.hp -= actual_dmg
        self.anim_dmg = actual_dmg

        # apply gimmick card effect
        if self.player.gimmick_card:
            for card in cards:
                if card.value == self.player.gimmick_card:
                    self._apply_gimmick_card_effect(card.value)
                    break

        # remove cards from hand
        for card in cards:
            self.player.hand.hand.remove(card)

        # refill hand
        cards_to_draw = self.player.hand_size - len(self.player.hand.hand)
        for _ in range(min(cards_to_draw, len(self.deck.deck))):
            self.player.hand.hand.append(self.deck.deck.pop())

        self.player.hand.hand.sort(key=lambda card: card.numeric_rank())

        if self.plays_remaining == 1 and self.boss.hp > 0:
            self.trigger_lose = True

        self.plays_remaining -= 1
        self.selected = set()

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
        if self.boss_index == 0:
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
        else:
            lines = [
                "Allowed sets this fight:",
                *[f"  - {s}" for s in self.allowed_sets],
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

    def _draw_played_cards(self):
        if self.anim_phase != 1 or not self.anim_cards:
            return

        for i, card in enumerate(self.anim_cards):
            x = int(self.anim_card_positions[i][0])
            y = int(self.anim_card_positions[i][1])
            self._draw_card(card, x, y, selected=False)

    def _apply_gimmick_card_effect(self, value):
        effect = GIMMICK_CARD_CONFIGS[value]["effect"]
        if effect == "bleed":
            self.boss.bleed_stacks += 1
            self.debug_event = f"BLEED APPLIED x{self.boss.bleed_stacks}"
            self.debug_event_timer = 120
        elif effect == "dmg_boost":
            self.anim_dmg = int(self.anim_dmg * 1.5)
            self.boss.hp -= int(self.anim_dmg * 0.5)  # apply the bonus damage
            self.message += "  DMG BOOST!"
        elif effect == "plays_up":
            if random.randint(0, 1) == 1:
                self.plays_remaining += 1
                self.message += "  +1 PLAY!"
        elif effect == "shuffles_up":
            if random.randint(0, 1) == 1:
                self.shuffles_remaining += 1
                self.message += "  +1 SHUFFLE!"

    def _load_boss_sprite(self):
        config = BOSS_CONFIGS[self.boss_index]
        try:
            sprite = pygame.image.load(resource_path(config["sprite"])).convert_alpha()
            return sprite
        except:
            return self._make_placeholder(80, 120, (180, 40, 40))

    # ── scene interface ───────────────────────────────────────

    def _point_in_circle(self, point, center):
        dx = point[0] - center[0]
        dy = point[1] - center[1]
        return (dx * dx + dy * dy) <= self.btn_radius ** 2

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                self.debug_mode = not self.debug_mode
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
                        self.sound_card_pickup.play()
                    return None

        if event.type == pygame.MOUSEWHEEL:
            self.hand_scroll -= event.y
            return None

        return None

    def update(self, dt):
        if self.anim_phase == 1:
            self.anim_timer -= 1
            all_arrived = True
            for i in range(len(self.anim_card_positions)):
                cx, cy = self.anim_card_positions[i]
                tx, ty = self.anim_card_targets[i]
                new_x = cx + (tx - cx) * self.ANIM_CARD_SPEED
                new_y = cy + (ty - cy) * self.ANIM_CARD_SPEED
                self.anim_card_positions[i] = [new_x, new_y]
                if abs(new_x - tx) > 1 or abs(new_y - ty) > 1:
                    all_arrived = False
            if self.anim_timer <= 0 or all_arrived:
                for i in range(len(self.anim_card_positions)):
                    self.anim_card_positions[i] = list(self.anim_card_targets[i])
                self.anim_phase = 2
                self.anim_timer = self.ANIM_SHOW_DAMAGE
            return None

        if self.anim_phase == 2:
            self.anim_timer -= 1

            if self.anim_boss_hp_display > self.boss.hp:
                self.anim_boss_hp_display = max(
                    self.boss.hp,
                    self.anim_boss_hp_display - self.ANIM_HP_SPEED
                )

            highest = max(card.numeric_rank() for card in self.anim_cards)
            base = base_damage_constant[self.anim_ddz_set]
            mult = self.player.damage_mult
            if self.anim_roll is not None:
                self.message = f"{self.anim_ddz_set.upper()}!  {highest} x {base} x {round(self.anim_roll, 1)} = {self.anim_dmg}"
            elif mult != 1:
                self.message = f"{self.anim_ddz_set.upper()}!  {highest} x {base} x {round(mult, 2)} = {self.anim_dmg}"
            else:
                self.message = f"{self.anim_ddz_set.upper()}!  {highest} x {base} = {self.anim_dmg}"
            self.msg_col = NEON_TEAL

            if self.anim_timer <= 0:
                self.anim_boss_hp_display = self.boss.hp
                self.anim_phase = 0
                self.message = f"{self.plays_remaining} plays left"
                self.msg_col = GREY

                if self.boss.hp <= 0:
                    self._next_boss()

            return None

        # normal update
        if self.trigger_lose:
            from scenes.lose_scene import LoseScene
            return LoseScene(self.screen, self.W, self.H, self.player)
        if self.pending_win:
            from scenes.lose_cutscene import LoseCutScene
            return LoseCutScene(self.screen, self.W, self.H)
        if self.pending_next_boss:
            self.pending_next_boss = False
            self._load_next_boss()
            from scenes.next_boss_scene import NextBossScene
            return NextBossScene(self.screen, self.W, self.H, self.boss_index, self)

        return None

    def draw(self):
        self.screen.blit(self.bg_image, (0, 0))
        # dark overlay for readability
        overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))  # increase last number for darker overlay
        self.screen.blit(overlay, (0, 0))
        self._draw_info()
        self._draw_sprites()
        self._draw_hand()
        self._draw_message()
        if self.anim_phase == 0:
            self._draw_play_button()
            self._draw_sort_button()
            self._draw_shuffle_button()
            self._draw_settings_button()
        self._draw_played_cards()
        self._draw_tutorial()