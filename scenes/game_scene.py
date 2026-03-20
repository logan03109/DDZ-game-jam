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


class GameScene:
    def __init__(self, screen, W, H):
        self.screen = screen
        self.W = W
        self.H = H

        # Fonts
        self.font_card_val  = pygame.font.SysFont("couriernew", 18, bold=True)
        self.font_card_sym  = pygame.font.SysFont("segoeui",    16)
        self.font_ui        = pygame.font.SysFont("couriernew", 22, bold=True)
        self.font_msg       = pygame.font.SysFont("couriernew", 28, bold=True)
        self.font_small     = pygame.font.SysFont("couriernew", 14)

        # Game state
        self.deck = Deck()
        self.deck.make_deck()
        self.player = Player(self.deck.deck)
        self.player.hand.hand.sort(key=lambda card: card.numeric_rank())

        self.selected = set()   # indices into self.player.hand.hand
        self.trigger_win = False
        self.trigger_lose = False
        self.message  = "Select cards and press PLAY"
        self.msg_col  = GREY
        self.msg_timer = 0      # how many frames to show message

        btn_w, btn_h = 180, 50
        self.play_btn = pygame.Rect(self.W // 2 - btn_w // 2, self.H - 80, btn_w, btn_h)
        self.sort_btn = pygame.Rect(self.W // 2 + btn_w // 2 + 20, self.H - 80, btn_w, btn_h)
        self.shuffle_btn = pygame.Rect(self.W // 2 - btn_w * 3 // 2 - 20, self.H - 80, btn_w, btn_h)
        self.play_hovered = False
        self.sort_hovered = False
        self.shuffle_hovered = False

        self.boss_index = 0
        self.boss = Boss(BOSS_CONFIGS[self.boss_index])
        self.allowed_sets = BOSS_CONFIGS[self.boss_index]["allowed_sets"]
        self.player_hand_size = BOSS_CONFIGS[self.boss_index]["hand_size"]
        self.plays_remaining = BOSS_CONFIGS[self.boss_index]["max_plays"]
        self.player = Player(self.deck.deck, self.player_hand_size)
        self.shuffles_remaining = BOSS_CONFIGS[self.boss_index]["max_shuffles"]

        self.plays_remaining = BOSS_CONFIGS[self.boss_index]["max_plays"]
        self.shuffles_remaining = BOSS_CONFIGS[self.boss_index]["max_shuffles"]

        self.trigger_next_boss_scene = False

        self.card_rects = []

        self.hand_scroll = 0  # number of cards to skip from the left

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
            label = "BIG" if card.value == "Big" else "SML"
            t1 = self.font_card_val.render(label, True, col)
            t2 = self.font_card_sym.render(sym,   True, col)
            self.screen.blit(t1, t1.get_rect(centerx=x + CARD_W // 2, top=draw_y + 8))
            self.screen.blit(t2, t2.get_rect(centerx=x + CARD_W // 2, top=draw_y + 34))
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

    def _draw_play_button(self):
        col = DARK_TEAL if self.play_hovered else (10, 35, 32)
        pygame.draw.rect(self.screen, col,       self.play_btn, border_radius=8)
        pygame.draw.rect(self.screen, NEON_TEAL, self.play_btn, 2, border_radius=8)
        label_col = NEON_TEAL if self.play_hovered else (160, 210, 200)
        txt = self.font_ui.render("[ PLAY ]", True, label_col)
        self.screen.blit(txt, txt.get_rect(center=self.play_btn.center))

    def _sort_hand(self):
        self.player.hand.hand.sort(key=lambda card: card.numeric_rank())
        self.selected = set()  # clear selection since indices change after sort

    def _draw_sort_button(self):
        col = (10, 35, 70) if self.sort_hovered else (10, 20, 45)
        pygame.draw.rect(self.screen, col, self.sort_btn, border_radius=8)
        pygame.draw.rect(self.screen, (0, 120, 220), self.sort_btn, 2, border_radius=8)
        label_col = (0, 180, 255) if self.sort_hovered else (100, 160, 210)
        txt = self.font_ui.render("[ SORT ]", True, label_col)
        self.screen.blit(txt, txt.get_rect(center=self.sort_btn.center))

    def _draw_shuffle_button(self):
        col = (45, 10, 60) if self.shuffle_hovered else (25, 5, 35)
        pygame.draw.rect(self.screen, col, self.shuffle_btn, border_radius=8)
        pygame.draw.rect(self.screen, (180, 0, 255), self.shuffle_btn, 2, border_radius=8)
        label_col = (200, 80, 255) if self.shuffle_hovered else (140, 60, 200)
        txt = self.font_ui.render("[ SHUFFLE ]", True, label_col)
        self.screen.blit(txt, txt.get_rect(center=self.shuffle_btn.center))

    def _shuffle_hand(self):
        if self.shuffles_remaining <= 0:
            self.message = "No shuffles remaining!"
            self.msg_col = RED
            return

        for card in self.player.hand.hand:
            self.deck.pool.append(card)
        self.player.hand.hand = []

        self.deck.redeck()

        for _ in range(self.player.shuffle_size):
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
            txt = self.font_msg.render(self.message, True, self.msg_col)
            self.screen.blit(txt, txt.get_rect(centerx=self.W // 2, centery=self.H - CARD_H - 140))

    def _draw_info(self):
        # Card counter — top left
        pygame.draw.rect(self.screen, PANEL_COL, (20, 20, 200, 50), border_radius=8)
        pygame.draw.rect(self.screen, BORDER_COL, (20, 20, 200, 50), 1, border_radius=8)
        card_count = self.font_small.render(
            f"CARDS LEFT: {len(self.deck.deck) + len(self.player.hand.hand)}", True, WHITE)
        self.screen.blit(card_count, card_count.get_rect(center=(120, 45)))

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
        self.screen.blit(plays_surf, plays_surf.get_rect(topleft=(20, 80)))

        shuffles_surf = self.font_small.render(f"SHUFFLES LEFT: {self.shuffles_remaining}", True, (200, 80, 255))
        self.screen.blit(shuffles_surf, shuffles_surf.get_rect(topleft=(20, 100)))

    def _next_boss(self):
        self.boss_index += 1
        if self.boss_index >= len(BOSS_CONFIGS):
            self.trigger_win = True
        else:
            config = BOSS_CONFIGS[self.boss_index]
            self.boss = Boss(config)
            self.allowed_sets = config["allowed_sets"]
            self.player_hand_size = config["hand_size"]
            self.plays_remaining = config["max_plays"]
            self.shuffles_remaining = config["max_shuffles"]
            self.trigger_next_boss_scene = True

    def on_resize(self, W, H):
        self.W = W
        self.H = H
        btn_w, btn_h = 180, 50
        self.play_btn = pygame.Rect(self.W // 2 - btn_w // 2, self.H - 80, btn_w, btn_h)
        self.sort_btn = pygame.Rect(self.W // 2 + btn_w // 2 + 20, self.H - 80, btn_w, btn_h)
        self.shuffle_btn = pygame.Rect(self.W // 2 - btn_w * 3 // 2 - 20, self.H - 80, btn_w, btn_h)
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

        dmg = damage_calc(cards, ddz_set, self.player.damage_mult)
        self.boss.hp -= int(dmg)

        # apply bleed
        if self.player.bleed > 0:
            self.boss.hp -= self.player.bleed

        # apply regen
        if self.player.regen > 0:
            self.player.hp = min(self.player.max_hp, self.player.hp + self.player.regen)

        for card in cards:
            self.player.hand.hand.remove(card)

        for _ in range(min(len(cards), len(self.deck.deck))):
            self.player.hand.hand.append(self.deck.deck.pop())

        self.player.hand.hand.sort(key=lambda card: card.numeric_rank())

        if self.plays_remaining == 1 and self.boss.hp > 0:
            self.trigger_lose = True

        self.plays_remaining -= 1
        self.selected = set()
        self.message = f"{ddz_set.upper()}!  -{int(dmg)} to boss  |  {self.plays_remaining} plays left"
        self.msg_col = NEON_TEAL

        if self.boss.hp <= 0:
            self._next_boss()

    # ── scene interface ───────────────────────────────────────

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.play_btn.collidepoint(event.pos):
                self._play_turn()
                return None
            if self.sort_btn.collidepoint(event.pos):
                self._sort_hand()
                return None
            if self.shuffle_btn.collidepoint(event.pos):
                self._shuffle_hand()
                return None

            # scroll arrows
            arrow_y = self.H - CARD_H - 60
            left_arrow = pygame.Rect(10, arrow_y, 30, 40)
            right_arrow = pygame.Rect(self.W - 40, arrow_y, 30, 40)
            if left_arrow.collidepoint(event.pos):
                self.hand_scroll -= 1
                return None
            if right_arrow.collidepoint(event.pos):
                self.hand_scroll += 1
                return None

            # card selection — now uses actual_index stored in card_rects
            for actual_index, rect in self.card_rects:
                if rect.collidepoint(event.pos):
                    if actual_index in self.selected:
                        self.selected.discard(actual_index)
                    else:
                        self.selected.add(actual_index)
                    return None

        # mouse wheel scrolling
        if event.type == pygame.MOUSEWHEEL:
            self.hand_scroll -= event.y
            return None

    def update(self, dt):
        if self.trigger_win:
            from scenes.win_scene import WinScene
            return WinScene(self.screen, self.W, self.H)
        if self.trigger_lose:
            from scenes.lose_scene import LoseScene
            return LoseScene(self.screen, self.W, self.H)
        if self.trigger_next_boss_scene:
            self.trigger_next_boss_scene = False
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