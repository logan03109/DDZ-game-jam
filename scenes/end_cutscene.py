# scenes/end_cutscene.py
import pygame
import cv2
from settings import resource_path, FONT_SIZE_SMALL

class EndCutScene:
    def __init__(self, screen, W, H):
        self.screen = screen
        self.W      = W
        self.H      = H

        self.font_small = pygame.font.SysFont("couriernew", FONT_SIZE_SMALL)

        pygame.mixer.music.load(resource_path("assets/audio/music/cutscene_audio.wav"))
        import settings as settings_module

        pygame.mixer.music.set_volume(settings_module.MUSIC_VOLUME * settings_module.MASTER_VOLUME)
        pygame.mixer.music.play()

        # load video
        self.cap             = cv2.VideoCapture(resource_path("assets/end_cutscene.mp4"))
        self.fps             = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_delay     = 1000 / self.fps
        self.last_frame_time = 0
        self.current_frame   = None
        self.done            = False

        # skip button
        btn_w, btn_h      = 120, 40
        self.skip_btn     = pygame.Rect(self.W - btn_w - 20, self.H - btn_h - 20, btn_w, btn_h)
        self.skip_hovered = False

    def on_resize(self, W, H):
        self.W        = W
        self.H        = H
        btn_w, btn_h  = 120, 40
        self.skip_btn = pygame.Rect(self.W - btn_w - 20, self.H - btn_h - 20, btn_w, btn_h)

    def _go_to_win(self):
        self.cap.release()
        pygame.mixer.music.stop()
        self.done = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.skip_hovered = self.skip_btn.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.skip_btn.collidepoint(event.pos):
                self._go_to_win()

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                self._go_to_win()

        return None

    def update(self, dt):
        if self.done:
            from scenes.win_scene import WinScene
            return WinScene(self.screen, self.W, self.H)

        self.last_frame_time += dt
        if self.last_frame_time >= self.frame_delay:
            self.last_frame_time = 0
            ret, frame = self.cap.read()
            if not ret:
                self._go_to_win()
                return None

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (self.W, self.H))
            frame = frame.swapaxes(0, 1)
            self.current_frame = pygame.surfarray.make_surface(frame)

        return None

    def draw(self):
        if self.current_frame:
            self.screen.blit(self.current_frame, (0, 0))
        else:
            self.screen.fill((0, 0, 0))

        col       = (40, 40, 40) if self.skip_hovered else (20, 20, 20)
        label_col = (160, 160, 160) if self.skip_hovered else (100, 100, 100)
        pygame.draw.rect(self.screen, col,         self.skip_btn, border_radius=6)
        pygame.draw.rect(self.screen, (80, 80, 80), self.skip_btn, 1, border_radius=6)
        txt = self.font_small.render("[ SKIP ]", True, label_col)
        self.screen.blit(txt, txt.get_rect(center=self.skip_btn.center))