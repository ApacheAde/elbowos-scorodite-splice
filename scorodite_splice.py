#!/usr/bin/env python3
"""Scorodite Splice — neon cable-bay joiner for ElbowOS. Python 3 + pygame.

Slide a splice clamp across four vertical bays. Weld chartreuse, cyan, and
amber jackets. Dodge rust live-faults. Not a ROM, not a clone of the
ElbowOS crane / pipe / prism packs.

  python3 scorodite_splice.py --play
  python3 scorodite_splice.py --record
"""
import math, os, random, subprocess, sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv and not RECORD
if not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/home/workdir/artifacts/SCORODITE_SPLICE_ElbowOS.mp4")
LANES = [150, 390, 630, 870]
CATCH, CLAMP_Y = 1468, 1505
COLS = {
    "lime": (186, 255, 74),
    "cyan": (72, 232, 214),
    "amber": (255, 176, 54),
    "fault": (255, 64, 58),
}
BG = (8, 18, 16)


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.quit()
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Scorodite Splice")
        self.font = pygame.font.SysFont("dejavusans", 64, bold=True)
        self.mid = pygame.font.SysFont("dejavusans", 42, bold=True)
        self.small = pygame.font.SysFont("dejavusans", 32, bold=True)
        self.reset(random.Random(11))

    def reset(self, rng):
        self.rng = rng
        self.clamp = 1
        self.cables = []
        self.sparks = []
        self.welds = []
        self.score = 0
        self.combo = 0
        self.flash = 0
        self.tick = 0
        self.spawn_in = 12
        self.jaw = 0.0

    def spawn(self):
        kind = "fault" if self.rng.random() < 0.24 else self.rng.choice(["lime", "cyan", "amber"])
        lane = self.rng.randrange(4)
        self.cables.append({"lane": lane, "y": 250.0, "kind": kind, "vy": 10.5 + self.tick * 0.006})

    def burst(self, lane, color):
        x = LANES[lane]
        for _ in range(14):
            ang = self.rng.random() * math.tau
            sp = self.rng.uniform(2, 9)
            self.sparks.append({
                "x": x, "y": CATCH, "vx": math.cos(ang) * sp, "vy": math.sin(ang) * sp - 2,
                "life": self.rng.randint(10, 22), "c": color,
            })

    def auto(self):
        threat = goal = None
        for c in self.cables:
            if c["kind"] == "fault" and c["y"] > 980:
                if threat is None or c["y"] > threat["y"]:
                    threat = c
            elif c["y"] > 640:
                if goal is None or c["y"] > goal["y"]:
                    goal = c
        if threat and threat["lane"] == self.clamp and threat["y"] > 1180:
            self.clamp = min(3, self.clamp + 1) if self.clamp < 2 else max(0, self.clamp - 1)
            return
        if goal and goal["lane"] != self.clamp:
            self.clamp += 1 if goal["lane"] > self.clamp else -1

    def step(self, move=0, auto=False):
        self.tick += 1
        self.flash = max(0, self.flash - 1)
        self.jaw = max(0.0, self.jaw - 0.1)
        if auto:
            self.auto()
        elif move:
            self.clamp = max(0, min(3, self.clamp + move))
        self.spawn_in -= 1
        if self.spawn_in <= 0:
            self.spawn()
            self.spawn_in = self.rng.randint(18, 30)
        kept = []
        for c in self.cables:
            c["y"] += c["vy"]
            if CATCH - 24 <= c["y"] <= CATCH + 30 and c["lane"] == self.clamp:
                if c["kind"] == "fault":
                    self.combo = 0
                    self.flash = 10
                    self.burst(c["lane"], COLS["fault"])
                else:
                    self.combo += 1
                    self.score += 40 * self.combo
                    self.jaw = 1.0
                    self.welds.append(c["kind"])
                    self.welds = self.welds[-16:]
                    self.burst(c["lane"], COLS[c["kind"]])
                continue
            if c["y"] > CATCH + 70:
                if c["kind"] != "fault":
                    self.combo = 0
                continue
            kept.append(c)
        self.cables = kept
        for s in self.sparks:
            s["x"] += s["vx"]
            s["y"] += s["vy"]
            s["vy"] += 0.25
            s["life"] -= 1
        self.sparks = [s for s in self.sparks if s["life"] > 0]

    def draw(self, surf):
        surf.fill(BG)
        pulse = (math.sin(self.tick * 0.08) + 1) * 0.5
        for i in range(8):
            y = int((self.tick * 3 + i * 240) % (H + 80)) - 40
            pygame.draw.rect(surf, (14, 36, 28), (0, y, W, 8))
        for i, x in enumerate(LANES):
            hot = i == self.clamp
            col = (36, 78, 58) if hot else (18, 40, 32)
            pygame.draw.rect(surf, col, (x - 70, 230, 140, 1280), border_radius=28)
            pygame.draw.rect(surf, (90, 160, 110) if hot else (40, 70, 54), (x - 70, 230, 140, 1280), 4, border_radius=28)
            pygame.draw.line(surf, (48, 110, 80), (x, 250), (x, 1460), 3)
            label = self.small.render(str(i + 1), True, (160, 220, 170))
            surf.blit(label, label.get_rect(center=(x, 280)))
        for c in self.cables:
            x, y = LANES[c["lane"]], int(c["y"])
            col = COLS[c["kind"]]
            pygame.draw.line(surf, col, (x, 240), (x, y - 28), 10)
            pygame.draw.circle(surf, col, (x, y), 28)
            pygame.draw.circle(surf, (255, 255, 230), (x, y), 10)
            if c["kind"] == "fault":
                pygame.draw.line(surf, (40, 8, 8), (x - 12, y - 12), (x + 12, y + 12), 4)
                pygame.draw.line(surf, (40, 8, 8), (x + 12, y - 12), (x - 12, y + 12), 4)
        cx = LANES[self.clamp]
        jaw = int(18 + self.jaw * 16)
        pygame.draw.rect(surf, (230, 255, 120), (cx - 78, CLAMP_Y, 156, 36), border_radius=10)
        pygame.draw.rect(surf, (120, 255, 190), (cx - 16, CLAMP_Y - jaw, 32, jaw + 8), border_radius=6)
        pygame.draw.circle(surf, (255, 255, 210), (cx, CLAMP_Y + 18), 10)
        for s in self.sparks:
            pygame.draw.circle(surf, s["c"], (int(s["x"]), int(s["y"])), max(2, s["life"] // 5))
        pygame.draw.rect(surf, (12, 28, 22), (40, 1580, 1000, 70), border_radius=16)
        for i, kind in enumerate(self.welds):
            pygame.draw.circle(surf, COLS[kind], (90 + i * 58, 1615), 22)
        if self.flash:
            veil = pygame.Surface((W, H), pygame.SRCALPHA)
            veil.fill((255, 40, 40, 50))
            surf.blit(veil, (0, 0))
        title = self.font.render("SCORODITE SPLICE", True, (210, 255, 140))
        surf.blit(title, title.get_rect(center=(W // 2, 90)))
        sub = self.small.render("neon cable bay", True, (120, 200, 160))
        surf.blit(sub, sub.get_rect(center=(W // 2, 150)))
        score = self.mid.render(f"SCORE  {self.score}", True, (255, 236, 170))
        surf.blit(score, score.get_rect(center=(W // 2, 1760)))
        combo = self.small.render(f"COMBO x{self.combo}", True, (72, 232, 214))
        surf.blit(combo, combo.get_rect(center=(W // 2, 1816)))
        tag = self.small.render("x.com/ElbowOS", True, (230, 255, 210))
        surf.blit(tag, tag.get_rect(center=(W // 2, 1872)))
        glow = int(40 + pulse * 40)
        pygame.draw.circle(surf, (glow, 180, 90), (cx, CLAMP_Y + 18), 46, 3)

    def play(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            move = 0
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN:
                    if ev.key in (pygame.K_ESCAPE, pygame.K_q):
                        running = False
                    elif ev.key in (pygame.K_LEFT, pygame.K_a):
                        move = -1
                    elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                        move = 1
                    elif ev.key == pygame.K_r:
                        self.reset(random.Random())
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                move = -1
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                move = 1
            self.step(move=move)
            self.draw(self.screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()

    def record(self):
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
            "-movflags", "+faststart", OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        self.reset(random.Random(11))
        try:
            for _ in range(FPS * SECS):
                self.step(auto=True)
                self.draw(self.screen)
                proc.stdin.write(pygame.image.tobytes(self.screen, "RGB"))
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1500:]}")
        print("wrote", OUT)
        pygame.quit()


def main():
    g = Game()
    if PLAY:
        g.play()
    else:
        g.record()


if __name__ == "__main__":
    main()
