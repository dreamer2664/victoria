# BOAT B — 25 ft Clinker Rowing Cutter

**What it is.** A 25 ft (7.620 m) wooden, clinker-built (lapstrake) ship's
rowing cutter, 10-oared, double-banked. The type is the standard Royal Navy
cutter of the second half of the nineteenth century: 25–34 ft, 8–14 men,
about 1½ tons, pulled with oars through rowlocks in the top strake, carried
on davits abreast the bridge.

The direct modelling reference is RMG SLR1818 (a varnished mahogany clinker
cutter, 917 mm long at 1:12), with RMG SLR0772 (cutter, c.1838) and SLR0719
(ship's boat, 1826 — carvel to port, clinker to starboard) as typological
companions. Evidence and its limits: `../HISTORICAL_EVIDENCE.md`.

---

## 1. Principal dimensions

| | metric | imperial |
|---|---|---|
| Length overall | 7.620 m | 25 ft 0 in |
| Beam, extreme | 1.905 m | 6 ft 3 in |
| Depth moulded amidships | 1.065 m | 3 ft 6 in |
| Sheer height at stem head | 0.908 m | 2 ft 11¾ in |
| Draught, light | 0.272 m | 10⅝ in |
| Draught, loaded | 0.397 m | 1 ft 3⅝ in |
| Displacement, light | 1017 kg | 1.00 ton |
| Displacement, loaded (10 men, gear, oars) | 1897 kg | 1.87 tons |
| Oars | 10 (5 thwarts, double-banked) | |
| Oar length | 3.66 m | 12 ft 0 in |

## 2. Hull — why it is built, not textured

The hull is **individually modelled overlapping strakes**, not a single
mesh with a wood texture:

* 11 strakes of 19 mm planking, each generated as its own solid band with a
  **8 mm land** on the strake below and its lower edge left proud of the one
  beneath — the lap that defines clinker work (`build_clinker_planking`,
  `n_strakes=11, thickness=0.019, lap=0.008`).
* Each strake is a closed solid with an outside face, an inside face and a
  visible land edge, so the shadows between strakes fall the way they do on
  the real thing; there is no normal map pretending.
* The seams are real geometry: 22 mm of overlap between adjacent strakes,
  which is what "clinch work" means and what Falconer describes in 1769.

Eight to thirteen strakes is the range on the surviving models; 11 is used
here to keep the strake widths close to the 150–200 mm of the reference
(SLR1818) at this hull depth.

## 3. Framing

* A grown oak keel with a raked stem and a sternpost.
* **Transverse frames** at 152 mm centres standing inside the planking,
  29 mm sided, from the keel to the sheer (`build_frames`), each following
  the real section of the hull at its own station — so no two frames are the
  same shape and the boat has the slight irregularity of a built boat.
* An internal keelson through the frames, and a **gunwale with a moulded cap
  rail** — a capping piece 6 mm proud of the rail beneath, 5 mm wider than it,
  with a rounded crown and a drip groove on the outboard side. The cap is
  built into the cross-section, so it carries a highlight along the whole
  length of the boat and reads as timber rather than as an extrusion.
* A raked transom built of separate transom planks.

The clinker boat's strength comes from the riveted overlap plus the frames;
the model shows both, which is why the interior reads as a boat and not as a
bathtub in the from-above render.

## 4. Fittings and furniture

* **Five thwarts** on XI = 0.235 … 0.675, each a 40 mm plank with a
  breast-hook and knees at the ends, resting on the frames — five thwarts is
  what the 1838 and 1826 references show, and two men to a thwart (one oar
  each) gives the 10-oared, double-banked arrangement.
* **Stern sheets** abaft the after thwart, with a stern bench and quarter
  knees.
* **Floor gratings**: slatted bottom boards, lifted 55 mm clear of the
  planking on cleats so bilge water can run under them and air can reach the
  frames — the "slatted floors on pegs" of the reference model.
* **Rowlocks** cut in the top strake, with bronze/tholes.
* **Mooring and lifting eyes**: two large keelson eyes fore and aft for the
  davit slings, plus stem and stern rings.
* **Mast clamp** on the bow thwart (SLR0719 shows exactly this), even though
  the boat is stowed without a mast.
* A boat hook and a bucket.

## 5. Oars and steering

* Ten oars, 3.66 m (12 ft) overall, each with a loom, a blade and a leather
  button, modelled as separate movable objects (`Oar_P1 … Oar_S5`).
* Each oar's **origin is on its rowlock axis**, so the exported GLB can be
  rotated about that point in Roblox to animate the stroke — this is why the
  parts are exported separately and why `manifest.json` records each pivot.
* The boat is steered by rowing: there is no rudder that matters at pulling
  speed, and the historical models show none. A steering sweep is carried as
  loose gear. In the Roblox model the port/starboard bank balance is what
  yaws the boat, which is how a coxswain actually steers a cutter.

## 6. Finish

Varnished mahogany **outside**, with the frames left bright and the
inside of the planking painted a pale buff — a common split on a working
boat's boat, where the inside takes the wear from boots, oars and bilge water
and the outside is kept bright because that is what the ship's company sees.
The glazing and varnish of the exterior is the finish of the reference model
(SLR1818). The Service painted its boats ship's-side grey from the 1900s, but
varnish is the better-documented finish for the 1880s and it shows the clinker
laps to advantage, which is the whole point of building them as geometry.

## 7. Rebuild

```
cd boats/scripts
LD_LIBRARY_PATH=/var/tmp/blender/lib blender -b --python build_rowing_cutter.py -- --quick
```

Flags: `--quick` (low-res renders), `--no-render`, `--oars-out` (ships the
oars in the rowlocks instead of stowed inboard).

## 8. Comparison with Boat A

The two boats are deliberately different vessels, not one hull twice:

| | steam cutter | rowing cutter |
|---|---|---|
| Beam | 2.134 m | 1.905 m |
| Depth amidships | 1.203 m | 1.065 m |
| Planking | carvel + double diagonal | clinker |
| Crew | 2–3 + passengers | 10 oarsmen |
| Freeboard (loaded) | 0.671 m | 0.668 m |

The steam boat is beamier and deeper because she has to carry 3.5 tonnes of
machinery, coal and water; the rowing boat is finer because ten men and their
oars are the load and the boat has to be light enough to row. Both sit at
about the same freeboard loaded, which is the design intent: they hang from
the same davits and look like a matched pair.
