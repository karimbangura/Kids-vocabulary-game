# ============================================
# components/button.py
# Reusable animated button for child UI
# ============================================
import pygame
from settings import (YELLOW_BTN, YELLOW_HOVER,
                      PURPLE_TEXT, WHITE, BLACK)


class Button:
    """
    Large child-friendly button.
    Supports pulse animation, hover glow,
    icon images and emoji labels.
    """

    def __init__(self, x, y, width, height,
                 text="",
                 image=None,
                 color=YELLOW_BTN,
                 hover_color=YELLOW_HOVER,
                 text_color=PURPLE_TEXT,
                 font_size=40,
                 border_radius=25):

        self.rect          = pygame.Rect(
            x, y, width, height)
        self.text          = text
        self.image         = image
        self.color         = color
        self.hover_color   = hover_color
        self.text_color    = text_color
        self.border_radius = border_radius
        self.font          = pygame.font.SysFont(
            "comicsansms", font_size, bold=True)

        # Animation state
        self._pulse        = 1.0
        self._pulse_dir    = 0.003
        self._hover_glow   = 0
        self.is_hovered    = False
        self.enabled       = True

        # Click flash
        self._flash        = 0

    # ── Draw ─────────────────────────────────
    def draw(self, surface):
        if not self.enabled:
            self._draw_disabled(surface)
            return

        col = (self.hover_color
               if self.is_hovered
               else self.color)

        # Flash white on click
        if self._flash > 0:
            col = WHITE
            self._flash -= 1

        # Pulse scale
        pw = int(self.rect.width  * self._pulse)
        ph = int(self.rect.height * self._pulse)
        px = self.rect.centerx - pw // 2
        py = self.rect.centery - ph // 2
        dr = pygame.Rect(px, py, pw, ph)

        # Shadow
        shadow = pygame.Surface(
            (pw + 6, ph + 6), pygame.SRCALPHA)
        pygame.draw.rect(
            shadow, (0, 0, 0, 60),
            (0, 0, pw + 6, ph + 6),
            border_radius=self.border_radius)
        surface.blit(shadow, (px + 3, py + 3))

        # Hover glow ring
        if self.is_hovered and self._hover_glow > 0:
            glow = pygame.Surface(
                (pw + 20, ph + 20),
                pygame.SRCALPHA)
            pygame.draw.rect(
                glow,
                (255, 220, 0,
                 int(self._hover_glow)),
                (0, 0, pw + 20, ph + 20),
                border_radius=self.border_radius + 5)
            surface.blit(glow,
                         (px - 10, py - 10))

        # Main button body
        pygame.draw.rect(surface, col, dr,
                         border_radius=self.border_radius)

        # Shine strip (top)
        shine = pygame.Surface(
            (pw - 20, ph // 3),
            pygame.SRCALPHA)
        shine.fill((255, 255, 255, 40))
        surface.blit(shine, (px + 10, py + 5))

        # Border
        pygame.draw.rect(surface, WHITE, dr,
                         3,
                         border_radius=self.border_radius)

        # Image
        if self.image:
            ir = self.image.get_rect(
                center=(dr.centerx,
                        dr.centery - 12))
            surface.blit(self.image, ir)

        # Text
        if self.text:
            lbl = self.font.render(
                self.text, True, self.text_color)
            lr  = lbl.get_rect(center=dr.center)
            if self.image:
                lr.top = dr.centery + 8
            surface.blit(lbl, lr)

    def _draw_disabled(self, surface):
        pygame.draw.rect(
            surface, (180, 180, 180),
            self.rect,
            border_radius=self.border_radius)
        if self.text:
            lbl = self.font.render(
                self.text, True,
                (120, 120, 120))
            lr  = lbl.get_rect(
                center=self.rect.center)
            surface.blit(lbl, lr)

    # ── Update ───────────────────────────────
    def update(self, mouse_pos):
        if not self.enabled:
            return
        self.is_hovered = self.rect.collidepoint(
            mouse_pos)

        # Pulse when hovered
        if self.is_hovered:
            self._pulse += self._pulse_dir
            if (self._pulse > 1.07
                    or self._pulse < 1.0):
                self._pulse_dir *= -1
            self._hover_glow = min(
                160, self._hover_glow + 15)
        else:
            self._pulse      = 1.0
            self._hover_glow = max(
                0, self._hover_glow - 10)

    # ── Click detection ───────────────────────
    def is_clicked(self, event) -> bool:
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(
                        event.pos):
                    self._flash = 6
                    return True
        return False