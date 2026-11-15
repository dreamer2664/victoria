# Realism pass — what changed and why

This records the pass that took the two cutters from "geometrically correct"
to "reads like a boat" in the renders. Every item below was driven by looking
at a render and finding it wanting, not by adding detail for its own sake.

## Render environment

The boats used to be photographed in a void: three studio softboxes, a dark
backdrop, no water. That is fine for a product shot and wrong for a boat — a
small open boat out of the water reads as a model on a shelf, and the eye has
no reference for scale or trim.

They are now shot **afloat on a sea plane at z = 0**, which is the load
waterline by the authoring convention. Two things follow:

* the renders double as a **draught check** — if the hydrostatics and the
  modelled hull disagreed, the boat would visibly float wrong;
* there is a horizon, a reflection and a contact shadow, which is most of what
  makes a rendered hull read as displacement rather than as a shape.

### The lighting lesson

The first three attempts to fix the water failed, for a reason worth recording:
**a bright parallelogram kept appearing across the sea.** It was diagnosed
first as water shading (raising roughness only made the smear bigger), then as
specular level, then as the lamp being visible in frame. The actual cause is
Fresnel: at the grazing angles a camera sees open water from, any lamp near the
horizon reflects almost totally, whatever its specular setting.

The rig that works (`bl.sea_studio`):

| Element | Setting |
|---|---|
| World | uniform sky, `(0.088, 0.108, 0.138)` at strength 2.6 |
| Sun | 0.30 m area, 2.6 × key energy, 58° elevation — small enough to reflect as a sparkle |
| Key | 4 m area, 0.7 × key energy, 20° elevation, overhead |
| Fill | **none** — the sky is the fill |
| Water | 4000 m plane, base `(0.010, 0.017, 0.024)`, roughness 0.30, specular IOR level 0.09, stretched noise bump |
| Grade | AgX, Medium High Contrast, exposure 0.20 |

No lamp may sit low: that is the whole rule.

## Boat A — steam cutter

**Canopy.** It was a flat painted board. It is now modelled as cloth: a 25 × 23
grid with 26 mm of sag between the six hoops, a ripple across the width, five
raised seams down its length, rope lacing through brass grommets to the
coaming, a scalloped three-row valance and closed end curtains. Canvas colour
was dropped from near-white to a dirty duck — a working boat's canopy is not a
yacht's.

**Lagging.** The main steam and exhaust runs are wrapped in canvas with brass
retaining bands. This is what a Victorian steam pipe actually looks like; bare
pipework read as scaffolding.

**Hull furniture.** Half-round rubbing strake along the topsides, brass band
down the fore side of the stem.

## Boat B — clinker rowing cutter

**Clinker laps.** The hull rendered as one varnished skin. Three separate
causes, all fixed:

1. *Shading.* The library default auto-smooth angle is 35°; a 13 mm lap on a
   19 mm plank meets the strake below at a shallower angle than that, so the
   shading smoothed straight over it. The planking now uses 20°.
2. *Colour.* All eleven strakes shared one material. Each now has its own
   timber with a small tone and warmth shift — the cue the eye uses to count
   strakes at a distance, long before it can resolve the lap itself.
3. *A strake that should not have been there.* The rubbing strake added for
   Boat A fouled this boat's gunwale and poked out into the air at the bow; it
   is gone. The brass stem band stays.

**Interior finish.** Was near-white paint; is now varnished timber to match the
outside, per the reference model.

**Gunwale.** Rewritten as a ten-point moulded section: crown standing 6 mm
proud of the rail beneath, 5 mm ear overhang, drip groove on the underside.
Built into the cross-section, so it carries a highlight the whole length of the
boat instead of reading as an extrusion.

**Floor gratings.** Lifted 55 mm onto cleats, so bilge water can run under them
and air can reach the frames.

## What was deliberately not done

* No wave model, spray or wake — the sea is a plane. The render is a portrait
  of the boat, not a sea state.
* No joinery: scarphs, fastenings and the way a cap rail is let down over the
  frame heads are not modelled. Correct at 1240 × 800, wrong at arm's length.
* No attempt to make the three-light studio rig work with water. It cannot:
  it is kept for the drawing sheets and the reference board, which have no
  water in them.

## Second pass — the boats themselves

The first pass was mostly environment. This one is all boat.

**Decks are planked, not painted.** Both decks were a single surface with a
wood texture, which reads as a painted floor at any angle. They are now laid
as individual boards (`hull.plank_panel`): constant board count along the
length so the planks converge at the ends the way stolen planks do, a 5 mm
caulking gap either side of each board, three timbers cycling through the run,
and closed ends so a board is a solid rather than a shell.

**Seats are held up by something.** Boat A's four thwarts were boxes hanging
in mid-air — the most common "3D model" tell in a small boat. They are now
moulded thwarts (crowned, tapered) landing on cleats let into the frames, with
a centre stanchion to the keelson under each of the two wide passenger
thwarts. The after seat's back-rest got its two arms for the same reason.

**The canopy is arched.** It rose only 30% more at the crown than at the edge,
which a real hoop frame never does. The cover and the brass hoops now follow a
circular arc (`sqrt(1 − 0.90 f²)`), so the canvas drops steeply at the sides
and the whole hood reads as tensioned over hoops.

**Fenders.** The old sine profile tapered the whole way and read as a peel
hanging on the topsides. A coir fender is a fat sausage with rounded ends: full
diameter through the middle, then a fast round-off.

**Boat B's boat hook** was stowed 40 mm outboard of the planking, which is why
a blade-shaped object appeared to lie on the topsides in every angle.

**Lighting.** Interiors were reading as black holes in the plan views — not
holes, as a ray cast confirmed, just unlit undersides of frames. A 9 m
overhead sky-port fills open boats without putting a lamp near the horizon.
