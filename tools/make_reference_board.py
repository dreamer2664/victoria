"""Build the annotated reference board (REQUIRED DELIVERABLE).

Assembles the primary historical material actually looked at during the
design, annotates each plate with what it was used for, and pairs every
plate with the modelling decision it justifies.  Output:

    reference/reference_board.png     (large annotated sheet)
    reference/reference_board.pdf
    reference/plates/                 (the individual plates, normalised)
"""
from __future__ import annotations
import os, sys, json, textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from PIL import Image

ROOT = "/home/user"
RES = os.path.join(ROOT, "research", "raw")
OUT = "/home/user/victoria/reference"

INK = "#2b2620"
PAPER = "#f7f3e8"

# (file, title, source, what it decided)
PLATES = [
    ("commons/Teutonic.png", "RMS Teutonic, 1889 — broadside",
     "Wikimedia Commons (PD)",
     "Sheer and freeboard; two buff funnels with black caps; three pole "
     "masts; the low midship house with an open promenade round it; "
     "Trotman davits with boats stowed above the promenade."),
    ("commons/RMS_Germanic_at_Liverpool.jpg", "RMS Germanic in the Mersey",
     "Wikimedia Commons (PD)",
     "Hull form and waterline; bow rake and counter stern; the black hull / "
     "white upper works division at the main deck."),
    ("commons/SS_Majestic__1890_.jpg", "SS Majestic, 1890",
     "Wikimedia Commons (PD)",
     "Deckhouse proportions and window rhythm; ventilator cowls; the sheer "
     "strake as a white band."),
    ("commons/The_Paris_in_Dry-Dock_Soton_1895_or_1896.jpg",
     "SS Paris in dry dock, 1895-96",
     "Wikimedia Commons (PD)",
     "Underwater body: keel, stem, sternpost, propeller aperture, rudder and "
     "the bilge keels.  Used for the hull section and the bow/stern detail."),
    ("commons/City_of_Paris__by_Antonio_Nicolo_Gasparo_Jacobsen.jpg",
     "City of Paris at sea (Jacobsen)",
     "Wikimedia Commons (PD)",
     "Sea keeping and the smoke plume at speed — the basis for the smoke "
     "and wake behaviour in the Roblox client script."),
    ("commons/SS_Paris_ex_City_of_Paris__1888_.jpg", "City of Paris, 1888",
     "Wikimedia Commons (PD)",
     "Alternative funnel/mast arrangement considered and rejected: twin "
     "screws and three masts read as a later ship."),
    ("ocean_magazine/Photo01-GrandStaircase-Teutonic-WhiteStarLine-500.jpg",
     "Grand staircase — Teutonic (Ocean Magazine, Sept 1889)",
     "Ocean: Magazine of Travel, Sept 1889",
     "Stair width, half landings, balustrade pattern and the glazed dome.  "
     "Our stair well is 4.7 m wide with a single flight per storey."),
    ("ocean_magazine/Photo02-SmokingSaloon-Teutonic-WhiteStarLine-500.jpg",
     "Smoking saloon — Teutonic (Ocean Magazine, Sept 1889)",
     "Ocean: Magazine of Travel, Sept 1889",
     "Panelled to the cornice, leather settees round the walls, small tables "
     "and revolving chairs; the fireplace as the focus of the room."),
    ("ocean_magazine/Photo04-Stateroom-Teutonic-WhiteStarLine-500.jpg",
     "First-class stateroom — Teutonic",
     "Ocean: Magazine of Travel, Sept 1889",
     "Berth proportions, wardrobe, washstand, and the window arrangement; "
     "our staterooms are 2.4 m wide x 3.1 m long with one berth abreast."),
    ("ocean_magazine/Photo05-MainSaloon-Teutonic-WhiteStarLine-500.jpg",
     "Main saloon — Teutonic (Ocean Magazine, Sept 1889)",
     "Ocean: Magazine of Travel, Sept 1889",
     "Long communal tables down the length; columns at the sides; the "
     "ground-glass panel that lights the saloon from the library table."),
    ("commons/SS_Teutonic__1889__-_Library.jpg", "Library — Teutonic",
     "Wikimedia Commons (PD)",
     "Bookcases and the central ground-glass table; used for our library "
     "6..27 m with a 4.9 x 2.9 m illuminating table."),
    ("commons/SS_Teutonic__1889__-_Staircase.jpg", "Second-class staircase — Teutonic",
     "Wikimedia Commons (PD)",
     "Cheaper joinery and a narrower stair for the second class, informing "
     "the second-class circulation we modelled."),
]

# Plate from the Gutenberg construction chapter (build sequence)
GUTENBERG_NOTE = (
    "Ocean Steamships (New York, 1891), chapter on construction, pp. 97-106 "
    "and its 105 plates were the authority for the BUILD SEQUENCE: keel "
    "laid, floors and frames erected, shell plating straked and riveted, "
    "stringers, bulkheads, deck beams, then the plating of the decks and the "
    "erection of the machinery.  Our hull module follows that order: "
    "keel/stem/sternpost, frames at 0.9144 m (3 ft) centres, 19 mm shell in "
    "1.83 m (6 ft) strakes, 14 watertight bulkheads."
)


def load(path, max_w=1400):
    p = os.path.join(RES, path)
    if not os.path.exists(p):
        return None
    im = Image.open(p).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, int(im.height * max_w / im.width)),
                       Image.LANCZOS)
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(os.path.join(OUT, "plates"), exist_ok=True)
    items = []
    for path, title, source, used in PLATES:
        im = load(path)
        if im is None:
            print("MISSING", path)
            continue
        name = os.path.basename(path)
        im.save(os.path.join(OUT, "plates", name), quality=92)
        items.append((im, title, source, used, name))

    ncol = 4
    nrow = (len(items) + ncol - 1) // ncol
    fig = plt.figure(figsize=(26, 6.4 * nrow + 3.2), dpi=150)
    fig.patch.set_facecolor(PAPER)
    gs = GridSpec(nrow, ncol, figure=fig, left=0.02, right=0.98,
                  top=1 - 0.9 / (6.4 * nrow + 3.2),
                  bottom=1.6 / (6.4 * nrow + 3.2), hspace=0.42, wspace=0.05)

    fig.text(0.02, 0.995, "SS AURELIAN (1889) — REFERENCE BOARD",
             fontsize=26, family="serif", weight="bold", va="top", color=INK)
    fig.text(0.02, 0.985,
             "Historical material actually examined. Every plate is paired with the modelling "
             "decision it justifies. Fictional vessel; period practice from British express "
             "liners of 1884-1890 (Teutonic, Majestic, Germanic, City of Paris, Umbria).",
             fontsize=9.5, va="top", color="#5c5347", style="italic")
    fig.text(0.98, 0.995, "Sheet 1 of 1", fontsize=10, ha="right",
             family="serif", color=INK, va="top")

    for i, (im, title, source, used, name) in enumerate(items):
        r, c = divmod(i, ncol)
        ax = fig.add_subplot(gs[r, c])
        ax.imshow(im)
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color("#8c7c5e"); s.set_linewidth(0.8)
        ax.set_title("%d.  %s" % (i + 1, title), fontsize=9.6, family="serif",
                     weight="bold", color=INK, pad=5)
        ax.text(0.0, -0.055,
                "\n".join(textwrap.wrap("REFERENCE: " + source, 62)) + "\n" +
                "\n".join(textwrap.wrap("USED FOR: " + used, 62)),
                transform=ax.transAxes, fontsize=6.6, va="top", color="#4a4237")

    # footer note on the construction authority
    fig.text(0.02, 0.012,
             "\n".join(textwrap.wrap(GUTENBERG_NOTE, 175)),
             fontsize=7.4, va="bottom", color="#4a4237")

    png = os.path.join(OUT, "reference_board.png")
    fig.savefig(png, facecolor=fig.get_facecolor())
    fig.savefig(png.replace(".png", ".pdf"), facecolor=fig.get_facecolor())
    plt.close(fig)
    print("wrote", png, fig.get_size_inches())

    with open(os.path.join(OUT, "reference_index.json"), "w") as fh:
        json.dump([{"file": n, "title": t, "source": s, "used_for": u}
                   for _, t, s, u, n in items], fh, indent=2)


if __name__ == "__main__":
    main()
