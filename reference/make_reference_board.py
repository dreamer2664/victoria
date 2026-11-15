#!/usr/bin/env python3
"""
make_reference_board.py -- builds reference/reference_board.html.

The board is a single self-contained HTML file: every plate is embedded as a
base64 data URI so it renders with no network access and survives being moved.
Each plate carries (a) its period caption, (b) what it actually shows, and
(c) the specific modelling decision it drove. Run from the repo root:

    python3 reference/make_reference_board.py
"""
import base64, io, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PLATES = os.path.join(HERE, "plates")

# (file, group, caption from the source, what it shows, decision it drove)
BOARD = [
 # ---------------------------------------------------------------- PORT A
 ("i_191.jpg", "Port A - passenger harbour", "Landing Stages at Liverpool",
  "A floating landing stage moored at the Liverpool waterfront, photographed from "
  "the river: a long timber and iron pontoon carried on pontoons, its deck crowded "
  "with passengers, gangways run up to it, and the sheds behind.",
  "Port A's landing stage is a floating pontoon on chains, not a fixed quay: the "
  "deck follows the tide, the <b>linkspan/gangway pair</b> connect it to the coping, "
  "and its length is set by the two berths it serves."),

 ("i_132.jpg", "Port A - passenger harbour", "The Gang-plank - just before sailing",
  "The enclosed embarkation gangway shipped against the ship's rail: a roofed, "
  "railed timber passage that keeps the passenger dry and, more to the point, "
  "funnels everyone past the ticket check.",
  "The terminal's <b>enclosed gangways</b> are modelled as roofed, railed passages "
  "with side screens - and the interaction trigger sits at the shore end, not the "
  "ship end."),

 ("i_142.jpg", "Port A - passenger harbour", "Revenue Officer Boarding, New York Bay",
  "A customs launch coming alongside with the revenue officer in the boat: boarding "
  "happens on the water, before the ship berths.",
  "Justifies a <b>customs launch berth</b> and a separate <b>customs &amp; immigration "
  "hall</b> with a one-way passenger route, rather than treating clearance as an "
  "abstract step."),

 ("i_145.jpg", "Port A - passenger harbour", "In the Steerage",
  "Steerage passengers on the open deck between the hatches, baggage in bundles - "
  "the traffic that actually paid for these ships.",
  "Drives the <b>baggage hall</b>, the wide plain circulation in the transit sheds, "
  "and the separate steerage/emigrant route around the terminal forecourt."),

 ("i_139.jpg", "Port A - passenger harbour", "The End of the Voyage",
  "Mail and baggage coming ashore over the rail at the end of the passage.",
  "Port A's quay apron is dimensioned for <b>baggage and mail handling</b>, not just "
  "passengers: hence the wide apron and the rail platform inside the shed line."),

 ("i_279.jpg", "Port A - passenger harbour", "Landing Passengers at Natal, South Africa",
  "Passengers landed by tender where there is no deep-water quay - the fallback "
  "arrangement of the period.",
  "Justifies Port A having <b>both</b> a deep-water berth (B1) and a shallow berth "
  "(B2) reached by tender from the landing stage."),

 ("i_115.jpg", "Port A - passenger harbour", "In the Grand Saloon of an Inman Steamer",
  "Panelling, columns, ceiling ribs and a cased skylight in an 1880s saloon.",
  "Supplies the <b>interior vocabulary of the booking hall</b>: panelled dado, "
  "cased beams, high clerestory, brass fittings."),

 ("i_227.jpg", "Port A - passenger harbour", "Unloading and Loading a Coastwise Steamer by Electric Light",
  "Cargo working at night under arc lamps: derrick, slings, packages stacked on the "
  "quay, men on the hatch coaming.",
  "Sets Port A's <b>cargo-shed and quay dressing</b>: packages, bales, barrels, "
  "winches and derricks along the quay edge, and lamp standards placed to light "
  "the working strip."),

 ("i_221.jpg", "Port A - passenger harbour", "Loading Grain from a Floating Elevator",
  "A floating elevator discharging alongside - the ship-to-quay machine of the era.",
  "Explains the <b>coal staithes and barge berths</b> on the far side of Port A: "
  "coaling was done from barges on the offside while passengers worked the main "
  "berth."),

 ("i_249.jpg", "Port A - passenger harbour", "A Cattle Steamship at Sea",
  "Cattle in pens on deck with slatted sides and fodder racks.",
  "Drives the <b>cattle pens</b> on the north quay: 2 ft 6 in by 8 ft pens, slatted, "
  "with a fenced race to the embarkation gate."),

 # ---------------------------------------------------------------- PORT B
 ("i_094.jpg", "Port B - industrial harbour", "The Umbria just before Launching",
  "A hull on the launch slip with all its staging, raking shores and props still in "
  "place, seen from the slip side.",
  "Port B's three <b>building slips</b> are dressed with keel blocks, raking shoring "
  "and staging - the slip is not left as a bare ramp."),

 ("i_099.jpg", "Port B - industrial harbour", "General View of the Frames of the City of New York, June 25 1887",
  "A bare steel skeleton on the stocks: frames, floors and beams only, with the "
  "erecting cranes and staging above.",
  "Justifies the slip appliances: <b>sheer legs and a Titan crane</b> serving the "
  "slips and the fitting-out quay, plus a plate-yard to the landward side."),

 ("i_102.jpg", "Port B - industrial harbour", "Frames of the City of New York, looking aft",
  "The internal volume of the frame - spacing, floors, and the shoring holding it.",
  "Sets the <b>moulding loft</b>'s job: full-size lofting of exactly these frames, "
  "hence a long top-lit floor and a floor-level interaction point."),

 ("i_103.jpg", "Port B - industrial harbour", "Frames of the City of New York, looking forward",
  "The same skeleton from the other end, crossing the slip head.",
  "Confirms the <b>slip width and head clearance</b> modelled: 34 m wide slips so a "
  "frame on the stocks can be walked around."),

 ("i_109.jpg", "Port B - industrial harbour", "The City of New York ready for Launching",
  "A complete hull on the ways, dog shores knocked away, ready to go.",
  "Port B's slips rake at <b>2.6 degrees</b> and run 96 m from the coping line down "
  "into the river - long enough for the specified 180 m hull only if launched in "
  "the conventional stern-first fashion, which is why the slip is fed from the top."),

 ("i_087.jpg", "Port B - industrial harbour", "Recent Naval Engine (Earle's Shipbuilding Company, Hull)",
  "An inverted vertical engine built in a shipyard shop: cylinders, guides, crank.",
  "The <b>engineering shop</b> and <b>boiler shop</b> are dimensioned around moving "
  "plant of this scale: 46 x 24 m bays with an overhead travelling crane gantry."),

 ("i_106.jpg", "Port B - industrial harbour", "The Manganese Bronze Propeller-Blade of the wrecked Mosel",
  "A single cast blade on the shop floor.",
  "Justifies the <b>plate and casting yard</b> stacks adjacent to the engineering "
  "shop, and the fitting-out quay where screws, rudders and shafts go aboard."),

 ("i_084.jpg", "Port B - industrial harbour", "The Twin Screws of the City of New York",
  "Twin screws and their shaft bosses under the counter.",
  "Drives the <b>fitting-out quay</b> interaction: the quay is where shafts, screws "
  "and rudders are shipped AFTER launch, so it needs deep water and a crane."),
]

SRC_NOTE = {
 "i_191.jpg": "p. 218", "i_132.jpg": "p. 133", "i_142.jpg": "p. 143",
 "i_145.jpg": "p. 146", "i_139.jpg": "p. 140", "i_279.jpg": "p. 280",
 "i_115.jpg": "p. 116", "i_227.jpg": "p. 226", "i_221.jpg": "p. 222",
 "i_249.jpg": "p. 250", "i_094.jpg": "p. 95", "i_099.jpg": "p. 100",
 "i_102.jpg": "p. 102", "i_103.jpg": "p. 104", "i_109.jpg": "p. 110",
 "i_087.jpg": "p. 88", "i_106.jpg": "p. 107", "i_084.jpg": "p. 85",
}


def thumb(path, width=760, quality=72):
    im = Image.open(path).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def main():
    rows = []
    group = None
    for fname, grp, cap, shows, decision in BOARD:
        p = os.path.join(PLATES, fname)
        if not os.path.exists(p):
            print("MISSING", fname)
            continue
        if grp != group:
            group = grp
            rows.append('<h2 class="grp">%s</h2>' % grp)
        rows.append(f"""
<figure class="plate">
  <img src="{thumb(p)}" alt="{cap}">
  <figcaption>
    <p class="cap"><b>{cap}.</b> <span class="cite">Ocean Steamships (New York, 1891),
      {SRC_NOTE.get(fname, '')}. Plate {fname.rsplit('.',1)[0]}.</span></p>
    <p class="shows"><span class="lbl">What it shows</span> {shows}</p>
    <p class="dec"><span class="lbl">Decision it drove</span> {decision}</p>
  </figcaption>
</figure>""")

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Operation Victoria &mdash; Historical Reference Board</title>
<style>
  :root {{ --ink:#1b1b19; --mut:#6d6a63; --rule:#d8d3c8; --paper:#f6f3ec; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--paper); color:var(--ink);
         font:15px/1.55 Georgia,'Times New Roman',serif; }}
  header {{ padding:44px 40px 26px; border-bottom:3px double var(--rule); }}
  h1 {{ margin:0 0 6px; font-size:27px; letter-spacing:.02em; }}
  .sub {{ color:var(--mut); font-size:14px; max-width:70ch; }}
  .grp {{ margin:0; padding:26px 40px 6px; font-size:13px; letter-spacing:.16em;
          text-transform:uppercase; color:#8a5a2b; border-top:1px solid var(--rule);
          background:#efeade; }}
  .plate {{ margin:0; padding:26px 40px; border-bottom:1px solid var(--rule);
            display:grid; grid-template-columns:minmax(280px,540px) 1fr; gap:28px;
            align-items:start; }}
  .plate img {{ width:100%; height:auto; display:block; border:1px solid #cbbfa8;
                filter:sepia(.12) contrast(1.02); }}
  figcaption {{ font-size:14px; }}
  .cap {{ margin:0 0 12px; font-size:15.5px; }}
  .cite {{ display:block; color:var(--mut); font-size:12.5px; font-style:italic;
           margin-top:3px; }}
  .lbl {{ display:inline-block; font-size:10.5px; letter-spacing:.12em;
          text-transform:uppercase; color:#8a5a2b; margin-right:8px;
          border-bottom:1px solid #d9c9a8; }}
  .shows {{ margin:0 0 10px; }}
  .dec {{ margion:0; background:#fffdf7; border-left:3px solid #b9905a;
          padding:10px 14px; }}
  footer {{ padding:30px 40px 60px; color:var(--mut); font-size:13px; }}
  @media (max-width:820px) {{ .plate {{ grid-template-columns:1fr; }} }}
</style></head><body>
<header>
  <h1>Operation Victoria &mdash; Historical Reference Board</h1>
  <p class="sub">Period photographs of the working machinery of the 1889 port, and the
  specific modelling decision each one drove. All plates are from <i>Ocean Steamships:
  A Popular Account of their Construction, Development, Management and Appliances</i>
  (New York, 1891), a public-domain work contemporaneous with the ports being built.
  Every plate below is a photograph or engraving made in or before 1891 &mdash; nothing
  later than 1889 has been used to justify a design decision.</p>
</header>
{''.join(rows)}
<footer>
  <p><b>Sourcing discipline.</b> These boards justify <i>form and arrangement</i>, not
  literal copying. Where a plate shows an American or Mediterranean arrangement the
  decision recorded beside it is the British-1889 adaptation actually modelled.</p>
  <p><b>Exclusions.</b> Belfast's Thompson Graving Dock (1911), the Arrol gantry
  (1905 onward) and Southampton's No. 5 dry dock (1896) are outside the 1889 horizon
  and are deliberately absent from both ports. See <code>HISTORICAL_EVIDENCE.md</code>.</p>
</footer>
</body></html>"""
    out = os.path.join(HERE, "reference_board.html")
    open(out, "w", encoding="utf-8").write(html)
    print("wrote", out, round(len(html) / 1e6, 2), "MB")


if __name__ == "__main__":
    main()
