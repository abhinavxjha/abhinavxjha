"""Tiny Pillow-based fake terminal that records every state as a GIF frame."""
import hashlib
import os
from PIL import Image, ImageDraw, ImageFont

BG = (13, 17, 23)
BAR = (22, 27, 34)
FG = (201, 209, 217)
GREEN = (63, 185, 80)
CYAN = (88, 166, 255)
YELLOW = (210, 153, 34)
PURPLE = (188, 140, 255)
DIM = (125, 133, 144)

FONT_PATHS = [
    os.path.join(os.path.dirname(__file__), "fonts", "mono.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/dejavu/DejaVuSansMono.ttf",
    "/Library/Fonts/Menlo.ttc",
    "C:/Windows/Fonts/consola.ttf",
]


def load_font(size):
    for path in FONT_PATHS:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    raise SystemExit("No monospace font found - drop one at fonts/mono.ttf")


class Terminal:
    def __init__(self, width=960, height=580, font_size=15, pad=18, title="terminal"):
        self.w, self.h, self.pad, self.title = width, height, pad, title
        self.font = load_font(font_size)
        self.cw = self.font.getlength("M")
        self.lh = font_size + 6
        self.bar_h = 34
        self.rows = int((height - self.bar_h - 2 * pad) // self.lh)
        self.lines, self.cur = [], []
        self.frames = []  # [rgb_bytes_hash, image, duration_ms]

    # ---------- drawing ----------
    def _render(self, cursor):
        img = Image.new("RGB", (self.w, self.h), BG)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, self.w, self.bar_h], fill=BAR)
        for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
            d.ellipse([16 + i * 22, 11, 28 + i * 22, 23], fill=c)
        d.text((self.w // 2, self.bar_h // 2), self.title, font=self.font, fill=DIM, anchor="mm")

        rows = (self.lines + [self.cur])[-self.rows:]
        y = self.bar_h + self.pad
        for i, segs in enumerate(rows):
            x = self.pad
            for text, color in segs:
                d.text((x, y), text, font=self.font, fill=color)
                x += len(text) * self.cw
            if cursor and i == len(rows) - 1:
                d.rectangle([x, y + 1, x + self.cw - 1, y + self.lh - 3], fill=FG)
            y += self.lh
        return img

    def snap(self, ms, cursor=True):
        img = self._render(cursor)
        key = hashlib.md5(img.tobytes()).digest()
        if self.frames and self.frames[-1][0] == key:
            self.frames[-1][2] += ms
        else:
            self.frames.append([key, img, ms])

    def pause(self, ms, cursor=True):
        self.snap(ms, cursor)

    # ---------- terminal actions ----------
    def write(self, text, color=FG):
        if self.cur and self.cur[-1][1] == color:
            self.cur[-1] = (self.cur[-1][0] + text, color)
        else:
            self.cur.append((text, color))

    def type(self, text, color=FG, per_char=60, mask=None):
        for ch in text:
            self.write(mask or ch, color)
            self.snap(per_char)

    def enter(self, ms=250):
        self.snap(ms)
        self.lines.append(self.cur)
        self.cur = []

    def out(self, segs, ms=45):
        if isinstance(segs, str):
            segs = [(segs, FG)]
        self.lines.append(segs)
        self.snap(ms, cursor=False)

    def prompt(self, user, host):
        self.write(f"{user}@{host}", GREEN)
        self.write(":", FG)
        self.write("~", CYAN)
        self.write("$ ", FG)
        self.snap(150)

    def save(self, path):
        imgs = [f[1] for f in self.frames]
        durs = [int(f[2]) for f in self.frames]
        imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=durs,
                     loop=0, optimize=True, disposal=1)
        return len(imgs), sum(durs) / 1000
