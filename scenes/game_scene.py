# scenes/game_scene.py
import pygame
from settings import W, H, suits, values
from entities.player import Player, validate_set, damage_calc
from entities.npc1 import Boss

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
    def __init__(self, screen):
        self.screen = screen

        # Fonts
        self.font_card_val  = pygame.font.SysFont("couriernew", 18, bold=True)
        self.font_card_sym  = pygame.font.SysFont("segoeui",    16)
        self.font_ui        = pygame.font.SysFont("couriernew", 22, bold=True)
        self.font_msg       = pygame.font.SysFont("couriernew", 28, bold=True)
        self.font_small     = pygame.font.SysFont("couriernew", 14)

        # Game state
        from entities.player import Deck   # import here to keep it tidy
        self.deck = Deck()
        self.deck.make_deck()
        self.player = Player(self.deck.deck)
        self.boss   = Boss()

        self.selected = set()   # indices into self.player.hand.hand
        self.message  = "Select cards and press PLAY"
        self.msg_col  = GREY
        self.msg_timer = 0      # how many frames to show message

        # Build button rects
        btn_w, btn_h = 180, 50
        self.play_btn = pygame.Rect(W // 2 - btn_w // 2, H - 80, btn_w, btn_h)
        self.play_hovered = False

        # Card rects — rebuilt every draw call
        self.card_rects = []

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
        total_w = len(hand) * (CARD_W + CARD_GAP) - CARD_GAP
        start_x = (W - total_w) // 2
        base_y  = H - CARD_H - 100

        self.card_rects = []
        for i, card in enumerate(hand):
            x = start_x + i * (CARD_W + CARD_GAP)
            rect = self._draw_card(card, x, base_y, selected=(i in self.selected))
            self.card_rects.append(rect)

    def _draw_play_button(self):
        col = DARK_TEAL if self.play_hovered else (10, 35, 32)
        pygame.draw.rect(self.screen, col,       self.play_btn, border_radius=8)
        pygame.draw.rect(self.screen, NEON_TEAL, self.play_btn, 2, border_radius=8)
        label_col = NEON_TEAL if self.play_hovered else (160, 210, 200)
        txt = self.font_ui.render("[ PLAY ]", True, label_col)
        self.screen.blit(txt, txt.get_rect(center=self.play_btn.center))

    def _draw_message(self):
        if self.message:
            txt = self.font_msg.render(self.message, True, self.msg_col)
            self.screen.blit(txt, txt.get_rect(centerx=W // 2, centery=H - CARD_H - 140))

    def _draw_info(self):
        """Top-left info panel — player HP and selected count."""
        lines = [
            f"HP      : {self.player.hp}",
            f"BOSS HP : {self.boss.hp}",
            f"SELECTED: {len(self.selected)} card(s)",
        ]
        pygame.draw.rect(self.screen, PANEL_COL,  (20, 20, 260, 90), border_radius=8)
        pygame.draw.rect(self.screen, BORDER_COL, (20, 20, 260, 90), 1, border_radius=8)
        for i, line in enumerate(lines):
            col = RED if ("HP" in line and self.player.hp < 300) else WHITE
            surf = self.font_small.render(line, True, col)
            self.screen.blit(surf, (32, 28 + i * 22))

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

        # Player attacks boss
        dmg = damage_calc(cards, ddz_set, self.player.damage_mult)
        self.boss.hp -= int(dmg)

        # Boss attacks back
        boss_dmg = self.boss.attack()
        self.player.hp -= boss_dmg

        # Play the cards (remove from hand, add to pool)
        for card in cards:
            self.player.hand.hand.remove(card)
            self.deck.pool.append(card)

        # Refill hand
        cards_used = len(cards)
        for _ in range(min(cards_used, len(self.deck.deck))):
            self.player.hand.hand.append(self.deck.deck.pop())

        self.selected = set()
        self.message  = f"{ddz_set.upper()}!  -{int(dmg)} to boss  -{boss_dmg} to you"
        self.msg_col  = NEON_TEAL

    # ── scene interface ───────────────────────────────────────

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.play_hovered = self.play_btn.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Play button
            if self.play_btn.collidepoint(event.pos):
                self._play_turn()
                return None

            # Card selection
            for i, rect in enumerate(self.card_rects):
                if rect.collidepoint(event.pos):
                    if i in self.selected:
                        self.selected.discard(i)
                    else:
                        self.selected.add(i)
                    return None

        return None

    def update(self, dt):
        # Scene transitions when someone dies
        if self.boss.hp <= 0:
            self.message = "YOU WIN!"
            self.msg_col = NEON_TEAL
            # return WinScene(self.screen) once you build it
        if self.player.hp <= 0:
            self.message = "YOU DIED"
            self.msg_col = RED
            # return LoseScene(self.screen) once you build it
        return None

    def draw(self):
        self.screen.fill(BG_COLOUR)
        self._draw_info()
        self._draw_hand()
        self._draw_message()
        self._draw_play_button()