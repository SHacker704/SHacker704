"""Generate assets/boot.gif with Pillow.

Run from any directory: python scripts/generate_boot.py
Install dependencies: python -m pip install -r scripts/requirements.txt
Use --font /path/to/a/monospace.ttf to override the platform font.
Use --preview-dir preview to export review frames and a verification report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 1200, 440
INK = (218, 229, 237)
BLUE = (142, 177, 200)
MUTED = (109, 128, 145)
LINE = (39, 54, 69)
DIAGNOSTICS = (
    "> MEMORY CHECK ........ OK",
    "> VISUAL INTERFACE .... OK",
    "> SYSTEM CORE ......... OK",
    "> SIGNAL .............. DETECTED",
    "> IDENTITY ............ SHacker704",
)


def find_font(override: Path | None) -> Path:
    if override:
        if not override.is_file():
            raise FileNotFoundError(override)
        return override
    candidates = (
        Path("C:/Windows/Fonts/CascadiaMono.ttf"),
        Path("C:/Windows/Fonts/consola.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf"),
        Path("/System/Library/Fonts/Menlo.ttc"),
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("No monospace font found. Pass --font path/to/font.ttf.")


class Display:
    def __init__(self, font: Path):
        self.font_path = font
        self.fonts: dict[int, ImageFont.FreeTypeFont] = {}
        self.background = self.make_background()
        self.frames: list[Image.Image] = []
        self.durations: list[int] = []
        self.labels: list[str] = []

    def font(self, size: int) -> ImageFont.FreeTypeFont:
        if size not in self.fonts:
            self.fonts[size] = ImageFont.truetype(str(self.font_path), size)
        return self.fonts[size]

    def text(self, draw, xy, value, size=32, color=INK):
        draw.text(xy, value, font=self.font(size), fill=color, anchor="lt")

    def make_background(self) -> Image.Image:
        image = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(image)
        for y in range(HEIGHT):
            # Quiet shading without noisy GIF dithering.
            level = int(4 * (1 - abs(y - HEIGHT / 2) / (HEIGHT / 2)))
            draw.line((0, y, WIDTH, y), fill=(8 + level, 13 + level, 20 + level))
        for x in range(32, WIDTH, 40):
            draw.line((x, 76, x, 416), fill=(17, 25, 34))
        for y in range(98, 417, 40):
            draw.line((32, y, 1168, y), fill=(17, 25, 34))
        draw.rectangle((24, 22, 1175, 417), outline=LINE)
        draw.line((24, 75, 1175, 75), fill=LINE)
        self.text(draw, (53, 38), "SH704", 24, BLUE)
        return image

    def layer(self) -> Image.Image:
        return Image.new("RGBA", (WIDTH, HEIGHT))

    def monogram(self, draw, ready=False):
        draw.line((911, 102, 911, 352), fill=LINE, width=1)
        # Custom geometric S and H, drawn as circuitry rather than a font logo.
        x, y = 967, 171
        tone = BLUE if ready else (78, 104, 124)
        draw.line(
            ((x + 62, y), (x, y), (x, y + 37), (x + 62, y + 37),
             (x + 62, y + 74), (x, y + 74)), fill=tone, width=7,
        )
        draw.line((x + 91, y, x + 91, y + 74), fill=tone, width=7)
        draw.line((x + 153, y, x + 153, y + 74), fill=tone, width=7)
        draw.line((x + 91, y + 37, x + 153, y + 37), fill=tone, width=7)
        self.text(draw, (1009, 267), "704", 32, tone)

    def boot(self, title="SH704 SYSTEM", status="INITIALIZING...", cursor=False):
        layer = self.layer()
        draw = ImageDraw.Draw(layer)
        self.monogram(draw)
        self.text(draw, (60, 122), title, 54)
        self.text(draw, (63, 208), status, 34, BLUE)
        if cursor:
            x = 63 + int(draw.textlength(status, font=self.font(34))) + 8
            draw.rectangle((x, 208, x + 15, 237), fill=BLUE)
        return layer

    def diagnostics(self, completed=5, partial="", cursor=False, progress=None):
        layer = self.layer()
        draw = ImageDraw.Draw(layer)
        self.monogram(draw)
        for index, line in enumerate(DIAGNOSTICS[:completed]):
            self.text(draw, (60, 99 + index * 38), line, 32)
        if partial:
            y = 99 + completed * 38
            self.text(draw, (60, y), partial, 32, BLUE)
            if cursor:
                x = 60 + int(draw.textlength(partial, font=self.font(32))) + 4
                draw.rectangle((x, y + 28, x + 16, y + 30), fill=BLUE)
        if progress is not None:
            self.text(draw, (60, 300), "LOADING VISUAL SHELL", 22, MUTED)
            left, top, right, bottom = 61, 335, 744, 354
            draw.line(((left + 5, top - 3), (left, top - 3), (left, bottom + 3),
                       (left + 5, bottom + 3)), fill=MUTED, width=2)
            draw.line(((right - 5, top - 3), (right, top - 3),
                       (right, bottom + 3), (right - 5, bottom + 3)), fill=MUTED, width=2)
            for index in range(40):
                x = left + 12 + index * 16.6
                color = BLUE if (index + 1) * 2.5 <= progress else (30, 43, 55)
                draw.rectangle((int(x), top, int(x) + 12, bottom), fill=color)
            self.text(draw, (777, 328), f"{progress:3d}%", 32, BLUE)
        return layer

    def ready(self):
        layer = self.layer()
        draw = ImageDraw.Draw(layer)
        self.monogram(draw, ready=True)
        size = 100
        while draw.textlength("SHacker704", font=self.font(size)) > 800:
            size -= 1
        font = self.font(size)
        nickname_x = 60 + (800 - draw.textlength("SHacker704", font=font)) / 2
        self.text(draw, (nickname_x, 160), "SHacker704", size)
        draw.line((65, 274, 856, 274), fill=LINE)
        self.text(draw, (65, 307), "SYSTEM READY", 32, BLUE)
        self.text(draw, (586, 310), "ACCESS GRANTED", 26, INK)
        return layer

    def compose(self, content: Image.Image):
        glow = content.filter(ImageFilter.GaussianBlur(3))
        glow.putalpha(glow.getchannel("A").point(lambda value: int(value * 0.12)))
        image = self.background.convert("RGBA")
        image = Image.alpha_composite(image, glow)
        image = Image.alpha_composite(image, content)
        scanlines = self.layer()
        draw = ImageDraw.Draw(scanlines)
        # Constant scanlines never flicker or sweep over the text.
        for y in range(25, HEIGHT - 22, 4):
            draw.line((25, y, WIDTH - 26, y), fill=(0, 0, 0, 15))
        return Image.alpha_composite(image, scanlines).convert("RGB")

    def add(self, content, duration=80, label=""):
        self.frames.append(self.compose(content))
        self.durations.append(duration)
        self.labels.append(label)

    def transition(self, first, second, steps=7, duration=60):
        for index in range(1, steps + 1):
            value = index / steps
            ease = value * value * (3 - 2 * value)
            self.add(Image.blend(first, second, ease), duration)

    def sequence(self):
        # The loop seam lands on the same readable initialization screen.
        first = self.boot("SH704", "", cursor=True)
        self.add(first, 250, "first")
        for length in (7, 9, 12):
            self.add(self.boot("SH704 SYSTEM"[:length], "", cursor=True), 100)
        for length in range(2, len("INITIALIZING...") + 1, 2):
            self.add(self.boot(status="INITIALIZING..."[:length], cursor=True), 90)
        boot = self.boot()
        self.add(boot, 260)
        self.transition(boot, self.diagnostics(0), steps=5)
        for index, line in enumerate(DIAGNOSTICS):
            for length in range(5, len(line), 5):
                self.add(self.diagnostics(index, line[:length], cursor=True), 60)
            self.add(self.diagnostics(index + 1), 140)
        self.add(self.diagnostics(), 240, "diagnostics")
        for progress in range(0, 101, 5):
            self.add(self.diagnostics(progress=progress), 60,
                     "loading" if progress == 60 else "")
        loaded = self.diagnostics(progress=100)
        self.add(loaded, 250)
        final = self.ready()
        self.transition(loaded, final, steps=9, duration=70)
        self.add(final, 3200, "ready")
        self.transition(final, first, steps=9, duration=70)

    def save(self, output: Path):
        output.parent.mkdir(parents=True, exist_ok=True)
        # One shared palette prevents colour pumping between diagnostic frames.
        selected = [self.labels.index(name) for name in ("first", "diagnostics", "loading", "ready")]
        atlas = Image.new("RGB", (WIDTH, HEIGHT * len(selected)))
        for row, index in enumerate(selected):
            atlas.paste(self.frames[index], (0, row * HEIGHT))
        palette = atlas.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
        frames = [frame.quantize(palette=palette, dither=Image.Dither.NONE)
                  for frame in self.frames]
        frames[0].save(output, save_all=True, append_images=frames[1:],
                       duration=self.durations, loop=0, optimize=True, disposal=1)
        # Locate samples by pixel hash, not a guessed frame number: Pillow merges
        # identical consecutive frames when encoding pauses.
        return {name: hashlib.sha256(frames[self.labels.index(name)].convert("RGB").tobytes()).hexdigest()
                for name in ("first", "diagnostics", "loading", "ready")}


class ImageReferences(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.sources.extend(value for name, value in attrs if name == "src")


def verify(output: Path, font: Path, sample_hashes: dict[str, str], preview: Path | None = None):
    """Verify the encoded GIF, rather than assuming source frames were all saved."""
    decoded: list[Image.Image] = []
    durations = []
    hashes = []
    with Image.open(output) as gif:
        assert gif.format == "GIF" and gif.size == (WIDTH, HEIGHT)
        assert gif.is_animated and gif.n_frames > 1
        assert gif.info.get("loop") == 0, "GIF must loop forever"
        for index in range(gif.n_frames):
            gif.seek(index)
            decoded.append(gif.convert("RGB"))
            durations.append(gif.info["duration"])
            hashes.append(hashlib.sha256(decoded[-1].tobytes()).hexdigest())
    assert output.stat().st_size <= 3_000_000, "GIF exceeds the 3 MB target"
    assert len(set(hashes)) > 20
    indices = {name: hashes.index(value) for name, value in sample_hashes.items()}
    ready_index = indices["ready"]
    assert durations[ready_index] >= 3000
    assert ImageChops.difference(decoded[0], decoded[-1]).getbbox() is None
    sources = ImageReferences()
    sources.feed((ROOT / "README.md").read_text(encoding="utf-8-sig"))
    assert sources.sources == ["./assets/boot.gif"], "Unexpected README image reference"
    assert (ROOT / sources.sources[0]).resolve() == output.resolve()
    report = {
        "file": output.relative_to(ROOT).as_posix(), "width": WIDTH, "height": HEIGHT,
        "frames": len(decoded), "duration_ms": sum(durations),
        "ready_hold_ms": durations[ready_index], "bytes": output.stat().st_size,
        "infinite_loop": True, "loop_seam_identical": True,
        "readme_image_exists": True, "font": font.name, "sample_frames": indices,
    }
    if preview is not None:
        frame_dir = preview / "frames"
        frame_dir.mkdir(parents=True, exist_ok=True)
        sheet = Image.new("RGB", (WIDTH, HEIGHT * len(indices)), (8, 13, 20))
        for row, (name, index) in enumerate(indices.items()):
            decoded[index].save(frame_dir / f"{name}.png")
            sheet.paste(decoded[index], (0, row * HEIGHT))
        sheet.save(preview / "contact-sheet.png")
        for name in ("ready", "diagnostics"):
            decoded[indices[name]].resize((375, round(HEIGHT * 375 / WIDTH)), Image.Resampling.LANCZOS).save(
                frame_dir / f"mobile-{name}.png")
        (preview / "verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", type=Path, help="Path to a TrueType/OpenType monospace font")
    parser.add_argument("--preview-dir", type=Path, help="Optional directory for review frames and report")
    args = parser.parse_args()
    font = find_font(args.font)
    display = Display(font)
    display.sequence()
    output = ROOT / "assets" / "boot.gif"
    sample_hashes = display.save(output)
    verify(output, font, sample_hashes, args.preview_dir)


if __name__ == "__main__":
    main()
