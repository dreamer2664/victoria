"""
signs.py -- painted signboards, fingerposts and notice boards as baked textures.

Victorian dock signage was painted lettering on timber or cast-iron boards. Baking
the lettering into a texture (rather than extruded text) keeps the geometry cheap
and lets the boards be instanced like any other modular asset.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# name -> (lines, board colour, letter colour, height_m, width_m, border)
SIGNS = {
    "harbour_board":   (["ALDERMOUTH", "HARBOUR BOARD"], (0.055, 0.075, 0.058),
                        (0.80, 0.74, 0.56), 1.30, 5.2, True),
    "custom_house":    (["H.M. CUSTOM HOUSE"], (0.72, 0.68, 0.58),
                        (0.075, 0.065, 0.055), 0.85, 5.0, False),
    "ravenna_line":    (["RAVENNA STEAMSHIP Co.", "LIVERPOOL  ·  NEW YORK  ·  BOSTON"],
                        (0.045, 0.055, 0.105), (0.85, 0.78, 0.52), 1.55, 7.5, True),
    "meridian_line":   (["MERIDIAN LINE"], (0.085, 0.045, 0.040),
                        (0.86, 0.80, 0.60), 1.10, 4.6, True),
    "albion_line":     (["ALBION & ATLANTIC", "STEAM NAVIGATION Co. Ltd."],
                        (0.040, 0.065, 0.085), (0.85, 0.82, 0.68), 1.45, 6.4, True),
    "no1_shed":        (["No 1 TRANSIT SHED", "BAGGAGE · MAILS"], (0.062, 0.062, 0.062),
                        (0.82, 0.80, 0.70), 0.80, 4.2, True),
    "tea_cotton":      (["TEA  ·  COTTON  ·  PRODUCE"], (0.085, 0.075, 0.060),
                        (0.80, 0.76, 0.64), 0.95, 6.0, False),
    "booking_office":  (["TICKETS", "BOOKING OFFICE"], (0.075, 0.085, 0.070),
                        (0.82, 0.78, 0.60), 0.95, 2.6, True),
    "customs_exam":    (["CUSTOMS EXAMINATION"], (0.70, 0.66, 0.56),
                        (0.06, 0.055, 0.05), 0.70, 4.0, False),
    "railway_station": (["ALDERMOUTH", "HARBOUR STATION"], (0.055, 0.075, 0.070),
                        (0.83, 0.79, 0.62), 1.20, 6.2, True),
    "coal_staithe":    (["HARBOUR BOARD", "COAL  STAITHE"], (0.058, 0.058, 0.058),
                        (0.80, 0.76, 0.66), 0.85, 3.6, True),
    "do_not_board":    (["NO UNAUTHORISED", "PERSONS BEYOND THIS POINT"],
                        (0.62, 0.56, 0.44), (0.07, 0.06, 0.05), 0.55, 2.2, False),
    "seamens_mission": (["SEAMEN'S MISSION"], (0.055, 0.062, 0.085),
                        (0.82, 0.78, 0.60), 0.70, 3.2, True),
    "chandlery":       (["SHIPPING CHANDLER"], (0.075, 0.062, 0.045),
                        (0.80, 0.74, 0.56), 0.70, 3.4, False),
    # shipyard
    "merrion":         (["MERRION  SHIPBUILDING", "&  ENGINEERING  Co.  Ltd."],
                        (0.052, 0.052, 0.055), (0.86, 0.82, 0.68), 1.9, 12.0, True),
    "no1_graving":     (["No 1 GRAVING DOCK", "A.D. 1867"], (0.058, 0.058, 0.058),
                        (0.80, 0.77, 0.66), 0.75, 3.4, True),
    "princess_dock":   (["THE PRINCESS GRAVING DOCK", "CAPACITY 800 FT · A.D. 1889"],
                        (0.050, 0.052, 0.058), (0.84, 0.80, 0.64), 0.90, 7.4, True),
    "time_office":     (["TIME OFFICE", "ALL HANDS IN BY 6.0 A.M."],
                        (0.062, 0.075, 0.062), (0.82, 0.78, 0.60), 0.85, 3.6, True),
    "engine_shop":     (["ENGINE  &  BOILER  SHOP"], (0.055, 0.055, 0.058),
                        (0.83, 0.79, 0.65), 0.85, 5.6, True),
    "moulding_loft":   (["MOULDING LOFT"], (0.055, 0.055, 0.058),
                        (0.83, 0.79, 0.65), 0.85, 3.8, True),
    "sawmill":         (["TIMBER  YARD  &  SAWMILL"], (0.070, 0.058, 0.042),
                        (0.82, 0.77, 0.60), 0.80, 5.0, True),
    "pump_house":      (["GRAVING  DOCK  PUMPING  ENGINE"], (0.058, 0.075, 0.062),
                        (0.83, 0.80, 0.64), 0.80, 5.4, True),
    "danger_crane":    (["DANGER", "OVERHEAD CRANE"], (0.62, 0.50, 0.18),
                        (0.08, 0.06, 0.05), 0.55, 1.8, False),
}

OUT = None


def _font(px, bold=True):
    try:
        return ImageFont.truetype(SERIF_B if bold else SANS_B, px)
    except Exception:
        return ImageFont.load_default()


def build_sign(name, outdir):
    lines, bg, fg, hm, wm, border = SIGNS[name]
    W = 1024
    H = max(96, int(W * hm / wm))
    img = Image.new("RGB", (W, H), tuple(int(c * 255) for c in bg))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(abs(hash(name)) % 9999)

    # painted-board grain / weathering
    arr = np.asarray(img).astype(np.float32)
    n = rng.random((H // 8 + 1, W // 8 + 1)).astype(np.float32)
    n = np.kron(n, np.ones((8, 8), np.float32))[:H, :W]
    arr *= (0.88 + 0.18 * n[..., None])
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)

    if border:
        inset = max(4, H // 22)
        d.rectangle([inset, inset, W - inset, H - inset], outline=tuple(
            int(c * 255) for c in fg), width=max(2, H // 60))

    # fit text: largest size that fits all lines
    n_lines = len(lines)
    pad = H * 0.24
    avail_h = H - 2 * pad
    best = None
    for px in range(int(avail_h / n_lines), 8, -1):
        f = _font(px)
        widths = [d.textlength(s, font=f) for s in lines]
        if max(widths) <= W * 0.86:
            best = (f, px, widths)
            break
    if best is None:
        best = (_font(10), 10, [d.textlength(s, font=_font(10)) for s in lines])
    f, px, widths = best
    lh = px * 1.16
    total = lh * n_lines
    y = (H - total) / 2
    for s, w in zip(lines, widths):
        x = (W - w) / 2
        d.text((x, y), s, font=f, fill=tuple(int(c * 255) for c in fg))
        y += lh

    # chipped paint / dirt spatter
    arr = np.asarray(img).astype(np.float32)
    chip = rng.random((H, W))
    chip = (chip < 0.0035)[..., None]
    arr = np.where(chip, arr * 0.55, arr)
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(
        os.path.join(outdir, "sign_" + name + ".png"))
    return "sign_" + name


def build_all(outdir):
    os.makedirs(outdir, exist_ok=True)
    made = []
    for name in SIGNS:
        made.append(build_sign(name, outdir))
    return made


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "textures/signs"
    names = build_all(out)
    print("Built %d sign textures -> %s" % (len(names), out))
