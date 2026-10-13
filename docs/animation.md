# SH704 boot display

The profile consists of one self-contained looping GIF and a short status line.
All diagnostics are part of a fictional boot interface. No external images,
statistics services, runtime scripts, or network requests are needed.

Current render with Cascadia Mono: 1200 × 440 pixels, 88 encoded frames,
10.27 seconds per loop, 507,931 bytes. Text is typed in short groups; the
40-segment progress bar fills from 0 to 100%. Static scanlines, a restrained
glow, a geometric SH monogram, and eased crossfades complete the display.

## Regenerate

Use Python 3.10 or newer:

```sh
python -m pip install -r scripts/requirements.txt
python scripts/generate_boot.py
```

The generator uses Cascadia Mono or Consolas on Windows, DejaVu Sans Mono or
Liberation Mono on Linux, and Menlo on macOS. Fonts are read from the local
system and are not redistributed. To select a different font:

```sh
python scripts/generate_boot.py --font /path/to/monospace.ttf
```

For an identical render, use the same font and Pillow version. Palette, dimensions,
diagnostic text, layout, and timings are defined in `scripts/generate_boot.py`.
GIF delays have 10 ms precision. Identical consecutive frames are merged,
so the final hold includes the 70 ms transition endpoint: 3.27 seconds.

The generator checks the encoded GIF's dimensions, animation, frame variation,
infinite loop, file size, final hold, identical loop seam, and the README image path.
It also exports a local contact sheet, sample PNGs (including 375 px views), and
`preview/verification.json`. These generated review files are ignored by Git.

## Preview

Open `preview/index.html` in a browser, or serve the repository:

```sh
python -m http.server 8040 --bind 127.0.0.1
```

Then open `http://127.0.0.1:8040/preview/`. The page shows the README composition
and a phone-width view on a light background. It uses the same GIF as the README.
The final screen holds for 3.27 seconds. The transition returns to the exact first
frame, so the loop boundary has no flash.

GitHub renders the relative `./assets/boot.gif` image in the profile README.
The new public profile can be checked after the commit is pushed to `main`;
local preview does not imply publication.

## Existing files

`docs/archive/README.previous.md` preserves the previous README byte for byte.
The original `cover.svg` is unchanged. Both also remain in Git history.
