# ============================================
# components/animator.py
# Smooth animation helpers
# Used for Zara and UI elements
# ============================================
import math


class FloatAnim:
    """Smooth up/down floating animation."""

    def __init__(self, base_y,
                 amplitude=15, speed=0.05):
        self.base_y    = base_y
        self.amplitude = amplitude
        self.speed     = speed
        self.t         = 0.0

    def update(self):
        self.t += self.speed
        return self.base_y + math.sin(
            self.t) * self.amplitude

    @property
    def y(self):
        return self.update()


class PulseAnim:
    """Smooth scale pulse animation."""

    def __init__(self, base=1.0,
                 amplitude=0.06, speed=0.05):
        self.base      = base
        self.amplitude = amplitude
        self.speed     = speed
        self.t         = 0.0

    def update(self) -> float:
        self.t += self.speed
        return (self.base +
                math.sin(self.t) * self.amplitude)

    @property
    def scale(self) -> float:
        return self.update()


class SlideAnim:
    """
    Smooth slide from start to target.
    Call update() each frame.
    """

    def __init__(self, start, target,
                 speed=0.12):
        self.value  = float(start)
        self.target = float(target)
        self.speed  = speed
        self.done   = False

    def update(self) -> float:
        diff = self.target - self.value
        if abs(diff) < 0.5:
            self.value = self.target
            self.done  = True
        else:
            self.value += diff * self.speed
        return self.value

    @property
    def val(self) -> float:
        return self.value


class StarCollect:
    """
    Animates a star flying from
    answer button to the score bar.
    """

    def __init__(self, start_x, start_y,
                 end_x, end_y):
        self.x      = float(start_x)
        self.y      = float(start_y)
        self.end_x  = float(end_x)
        self.end_y  = float(end_y)
        self.done   = False
        self.size   = 30

    def update(self):
        dx = self.end_x - self.x
        dy = self.end_y - self.y
        dist = (dx**2 + dy**2) ** 0.5
        if dist < 5:
            self.done = True
            return
        speed = min(18, max(6, dist * 0.15))
        self.x += (dx / dist) * speed
        self.y += (dy / dist) * speed
        self.size = max(
            8, self.size - 0.5)

    def draw(self, surface):
        import pygame
        if self.done:
            return
        s    = int(self.size)
        font = pygame.font.SysFont(
            "segoeuiemoji", s)
        star = font.render("⭐", True,
                           (255, 220, 0))
        surface.blit(star,
                     (int(self.x) - s // 2,
                      int(self.y) - s // 2))