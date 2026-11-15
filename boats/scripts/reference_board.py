"""
reference_board.py -- the annotated historical reference board.

Lays out the reference photographs beside the finished model renders, with a
caption for each saying what was taken from it. Runs on plain python (PIL).

    python3 reference_board.py
"""

import os

from PIL import Image, ImageDraw, ImageFont

ROOT = "/home/user/victoria"
REFS = os.path.join(ROOT, "refs", "rmg")
RENDERS = os.path.join(ROOT, "boats", "renders")
OUT = os.path.join(ROOT, "boats", "drawings", "reference_board.png")

W, H = 3400, 2380
BG = (250, 249, 246)
INK = (26, 26, 26)
GREY = (90, 90, 90)
ACCENT = (140, 28, 19)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except Exception:
        return ImageFont.load_default()


def fit(im, w, h):
    im = im.convert("RGB")
    s = min(w / im.width, h / im.height)
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))),
                     Image.LANCZOS)


def panel(d, x, y, w, h, img_path, title, caption, num=None, crop=None):
    d.rectangle([x, y, x + w, y + h], outline=(210, 208, 202), width=2)
    ih = h - 150
    if os.path.exists(img_path):
        im = Image.open(img_path)
        if crop:
            im = im.crop(crop)
        im = fit(im, w - 24, ih - 12)
        board.paste(im, (x + (w - im.width) // 2, y + 12))
    ty = y + ih + 6
    if num is not None:
        d.ellipse([x + 14, ty + 4, x + 44, ty + 34], fill=ACCENT)
        n = str(num)
        tw = d.textlength(n, font=font(20, True))
        d.text((x + 29 - tw / 2, ty + 8), n, font=font(20, True), fill=(255, 255, 255))
        tx = x + 54
    else:
        tx = x + 14
    d.text((tx, ty + 2), title, font=font(21, True), fill=INK)
    # wrap the caption
    words = caption.split()
    lines, cur = [], ""
    maxw = w - tx + x - 16
    for word in words:
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font(17)) > maxw:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    for i, line in enumerate(lines[:4]):
        d.text((tx, ty + 30 + i * 22), line, font=font(17), fill=GREY)


board = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(board)

# ---- header ----
d.rectangle([0, 0, W, 132], fill=(24, 26, 30))
d.text((60, 34), "OPERATION VICTORIA  ·  SHIP'S BOATS  ·  HISTORICAL REFERENCE BOARD",
       font=font(38, True), fill=(255, 255, 255))
d.text((60, 88), "Period 1889 · the reference material actually consulted, and what was taken from it",
       font=font(22), fill=(190, 190, 190))
d.text((W - 470, 44), "1889  |  Boat Department", font=font(24, True), fill=(210, 190, 140))
d.text((W - 470, 82), "Scale 1:1 as modelled, metres", font=font(19), fill=(160, 160, 160))

# ---- row 1: references ----
y0 = 170
d.text((60, y0), "1 · THE REFERENCE MATERIAL", font=font(26, True), fill=ACCENT)
y0 += 46
pw, ph = 1060, 700
gap = 40
xs = [60, 60 + pw + gap, 60 + 2 * (pw + gap)]

panel(d, xs[0], y0, pw, ph, os.path.join(REFS, "e9006_221.jpg"),
      "RMG SLR0772 — cutter, c.1838",
      "Admiralty half-model, 1:24. Source for the double-diagonal build, five "
      "thwarts, stern seating and the rudder and tiller carried by a boat of "
      "this family. A typological reference only: 51 years earlier than 1889.", 1)
panel(d, xs[1], y0, pw, ph, os.path.join(REFS, "f8825_002.jpg"),
      "RMG SLR1818 — clinker cutter",
      "Varnished mahogany, 917 mm at 1:12. The principal reference for Boat B: "
      "lapstrake planking, oak frames standing inside the strakes, thwarts on "
      "the frames, slatted floors on pegs, and the pair of keelson eyes for "
      "the davit slings.", 2)
panel(d, xs[2], y0, pw, ph, os.path.join(REFS, "f8933_002.jpg"),
      "RMG SLR0719 — ship's boat, 1826",
      "John Hayes, carvel to port and clinker to starboard on one hull: a "
      "direct comparison of the two builds, with five thwarts, six oars and a "
      "mast clamp on the bow thwart.", 3)

# ---- row 2: the models ----
y1 = y0 + ph + 70
d.text((60, y1), "2 · THE FINISHED MODELS", font=font(26, True), fill=ACCENT)
y1 += 46
pw2 = (W - 120 - gap) // 2
panel(d, 60, y1, pw2, 720, os.path.join(RENDERS, "steam_hero.png"),
      "Boat A — 25 ft steam cutter",
      "Carvel planking over a double-diagonal inner skin, white sheer strake, "
      "coal-fired vertical boiler and inverted vertical engine under a canvas "
      "canopy carried on the coaming, funnel through the canvas, two-bladed "
      "screw and plate rudder aft.", 4)
panel(d, 60 + pw2 + gap, y1, pw2, 720, os.path.join(RENDERS, "rowing_hero.png"),
      "Boat B — 25 ft clinker rowing cutter",
      "Eleven individually modelled overlapping strakes with a 22 mm land, oak "
      "frames at 152 mm centres inside the planking, five thwarts, stern "
      "sheets, floor gratings, ten 12 ft oars and a transom-hung plate rudder.", 5)

# ---- row 3: element comparisons ----
y2 = y1 + 720 + 70
d.text((60, y2), "3 · ELEMENT COMPARISONS  (reference above, model below)",
       font=font(26, True), fill=ACCENT)
y2 += 46
pw3, ph3 = (W - 120 - 3 * gap) // 4, 560

# clinker strakes: reference crop of the topsides vs our model's topsides
panel(d, 60, y2, pw3, ph3, os.path.join(REFS, "f8825_001.jpg"),
      "Clinker lapstrake",
      "Reference: distinct overlapping lands, each strake proud of the one "
      "below. (RMG SLR1818, topsides.)", 6)
panel(d, 60 + pw3 + gap, y2, pw3, ph3,
      os.path.join(RENDERS, "rowing_broadside.png"),
      "Model: Boat B topsides",
      "Each of the 11 strakes is a closed solid with its own land, so the "
      "shadow line between strakes is real geometry, not a texture.", 7)
panel(d, 60 + 2 * (pw3 + gap), y2, pw3, ph3,
      os.path.join(REFS, "e9006_222.jpg"),
      "Interior arrangement",
      "Reference: thwarts on the frames, framing standing proud, floorboards "
      "clear of the planking. (RMG SLR0772.)", 8)
panel(d, 60 + 3 * (pw3 + gap), y2, pw3, ph3,
      os.path.join(RENDERS, "rowing_from_above.png"),
      "Model: Boat B interior",
      "The same arrangement built as geometry: five thwarts with knees, stern "
      "sheets, and floor gratings on cleats over the frames.", 9)

# ---- footer ----
fy = H - 150
d.rectangle([0, fy, W, H], fill=(238, 236, 230))
d.text((60, fy + 26),
       "Reference photographs: Royal Museums Greenwich (SLR0772, SLR1818, SLR0719). "
       "Model renders: this project.",
       font=font(19), fill=GREY)
d.text((60, fy + 58),
       "The 1888 Admiralty plan for the 25 ft steam cutter (RMG NPC9572) has no "
       "publicly available image; Boat A's hull lines are therefore a reconstruction "
       "to the published principal dimensions, and its equipment a documented-type "
       "reconstruction. See HISTORICAL_EVIDENCE.md.",
       font=font(19), fill=ACCENT)
d.text((60, fy + 96),
       "Nothing on this board is a copy of a surviving hull: all geometry is generated "
       "from designed curves in boats/scripts/boatgen.",
       font=font(19), fill=GREY)

board.save(OUT)
board.save(OUT.replace(".png", "_small.png"), quality=90)
print("wrote", OUT)
