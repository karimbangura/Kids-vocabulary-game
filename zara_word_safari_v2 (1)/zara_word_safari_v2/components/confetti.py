# ============================================
# components/confetti.py
# Enhanced confetti particle system
# Stars, circles, rectangles, ribbons, emojis
# ============================================
import pygame
import random
import math
from settings import CONFETTI_COLS


class Confetti:
    SHAPES  = ["rect", "circle", "star", "ribbon", "diamond"]
    EMOJIS  = ["⭐", "🎉", "🌟", "✨", "🎊", "💫", "🏆", "🎈"]

    def __init__(self, screen_w, screen_h):
        self.screen_w     = screen_w
        self.screen_h     = screen_h
        self.particles    = []
        self.emoji_bursts = []   # floating emoji particles
        self.active       = False

        # Emoji font for burst particles
        self.f_emoji_sm = pygame.font.SysFont("segoeuiemoji", 36)
        self.f_emoji_lg = pygame.font.SysFont("segoeuiemoji", 56)

    def trigger(self, count=180):
        """Fire confetti from top + emoji burst from centre."""
        self.active = True

        # ── Confetti rain from top ────────────
        for _ in range(count):
            self.particles.append({
                "x"      : random.randint(0, self.screen_w),
                "y"      : random.randint(-160, -5),
                "dx"     : random.uniform(-3.0, 3.0),
                "dy"     : random.uniform(2.5, 8.0),
                "size"   : random.randint(9, 26),
                "color"  : random.choice(CONFETTI_COLS),
                "rot"    : random.randint(0, 360),
                "drot"   : random.uniform(-9, 9),
                "shape"  : random.choice(self.SHAPES),
                "gravity": random.uniform(0.04, 0.18),
                "alpha"  : 255,
            })

        # ── Emoji burst from screen centre ────
        cx = self.screen_w  // 2
        cy = self.screen_h  // 2
        for _ in range(22):
            angle  = random.uniform(0, math.pi * 2)
            speed  = random.uniform(4, 14)
            big    = random.random() < 0.4
            self.emoji_bursts.append({
                "x"    : cx,
                "y"    : cy,
                "dx"   : math.cos(angle) * speed,
                "dy"   : math.sin(angle) * speed - random.uniform(2, 6),
                "emoji": random.choice(self.EMOJIS),
                "font" : self.f_emoji_lg if big else self.f_emoji_sm,
                "life" : random.randint(55, 90),
                "max"  : 90,
                "scale": random.uniform(0.8, 1.4),
                "rot"  : random.uniform(-180, 180),
                "drot" : random.uniform(-6, 6),
                "gravity": 0.25,
            })

    def trigger_burst(self, x, y, count=40):
        """Extra localised burst (e.g. on correct button)."""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(3, 10)
            self.particles.append({
                "x"      : x,
                "y"      : y,
                "dx"     : math.cos(angle) * speed,
                "dy"     : math.sin(angle) * speed - random.uniform(1, 4),
                "size"   : random.randint(7, 18),
                "color"  : random.choice(CONFETTI_COLS),
                "rot"    : random.randint(0, 360),
                "drot"   : random.uniform(-10, 10),
                "shape"  : random.choice(self.SHAPES),
                "gravity": random.uniform(0.1, 0.25),
                "alpha"  : 255,
            })

    def update(self):
        if not self.active:
            return

        # Confetti
        alive = []
        for p in self.particles:
            p["x"]   += p["dx"]
            p["y"]   += p["dy"]
            p["dy"]  += p["gravity"]
            p["rot"] += p["drot"]
            p["dx"]  *= 0.995   # slight air resistance
            if p["y"] < self.screen_h + 60:
                alive.append(p)
        self.particles = alive

        # Emoji bursts
        alive_e = []
        for e in self.emoji_bursts:
            e["x"]   += e["dx"]
            e["y"]   += e["dy"]
            e["dy"]  += e["gravity"]
            e["rot"] += e["drot"]
            e["life"] -= 1
            if e["life"] > 0:
                alive_e.append(e)
        self.emoji_bursts = alive_e

        if not self.particles and not self.emoji_bursts:
            self.active = False

    # ── Shape helpers ─────────────────────────
    def _star_points(self, cx, cy, r, rot):
        pts = []
        for i in range(10):
            angle = math.radians(rot + i * 36 - 90)
            rad   = r if i % 2 == 0 else r * 0.42
            pts.append((
                cx + rad * math.cos(angle),
                cy + rad * math.sin(angle)))
        return pts

    def _diamond_points(self, cx, cy, r, rot):
        angles = [0, 90, 180, 270]
        pts = []
        for a in angles:
            rad = math.radians(a + rot)
            pts.append((
                cx + r * math.cos(rad),
                cy + r * math.sin(rad)))
        return pts

    def draw(self, surface):
        if not self.active:
            return

        # ── Draw confetti particles ───────────
        for p in self.particles:
            s  = p["size"]
            cx = int(p["x"])
            cy = int(p["y"])
            c  = p["color"]

            if p["shape"] == "rect":
                surf = pygame.Surface(
                    (s, max(4, s // 3)),
                    pygame.SRCALPHA)
                surf.fill((*c, 220))
                rot  = pygame.transform.rotate(
                    surf, p["rot"])
                surface.blit(rot, (cx - rot.get_width()  // 2,
                                   cy - rot.get_height() // 2))

            elif p["shape"] == "circle":
                pygame.draw.circle(
                    surface, c, (cx, cy), s // 2)
                # inner highlight
                pygame.draw.circle(
                    surface, (255, 255, 255),
                    (cx - s // 6, cy - s // 6),
                    max(2, s // 6))

            elif p["shape"] == "star":
                pts = self._star_points(cx, cy, s, p["rot"])
                if len(pts) >= 3:
                    pygame.draw.polygon(surface, c, pts)

            elif p["shape"] == "ribbon":
                surf = pygame.Surface(
                    (s * 2, max(3, s // 4)),
                    pygame.SRCALPHA)
                surf.fill((*c, 200))
                rot  = pygame.transform.rotate(
                    surf, p["rot"])
                surface.blit(rot, (cx - rot.get_width()  // 2,
                                   cy - rot.get_height() // 2))

            elif p["shape"] == "diamond":
                pts = self._diamond_points(cx, cy, s, p["rot"])
                pygame.draw.polygon(surface, c, pts)

        # ── Draw emoji bursts ─────────────────
        for e in self.emoji_bursts:
            alpha  = int(255 * (e["life"] / e["max"]))
            alpha  = max(0, min(255, alpha))
            try:
                es = e["font"].render(e["emoji"], True, (255, 255, 255))
                # fade out
                es.set_alpha(alpha)
                surface.blit(
                    es,
                    (int(e["x"]) - es.get_width()  // 2,
                     int(e["y"]) - es.get_height() // 2))
            except Exception:
                pass
