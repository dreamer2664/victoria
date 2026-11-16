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

## Boat C — 27 ft whaler

**The double end.** A whaler has no transom and no sternpost: both ends are
stem, and the after body is the fore body mirrored. It was worth getting right
because it changes every line on the boat — sheer, waterline and section shape
all run through amidships and repeat aft. The strakes are therefore laid as one
continuous run from stem to stem over 76 stations and nine strakes, not as a
fore body and an after body, so the two ends cannot drift apart: there is only
one curve.

**No transom, and no seat trying to be one.** On a transom boat the after
thwart can sit on the counter; here there is no counter to sit on. The four
pulling thwarts are narrow 245 mm moulded planks, the aftermost furniture is a
340 mm stern-sheets bench set athwartships at 0.83 of the length, and two side
benches flank the centreboard trunk for the passengers. `verify.py` asserts
there is no object named `Transom` on this hull, which is a cheap guard against
a later edit quietly giving the boat a flat stern.

**The drop keel is drawn up.** The centreboard is a trunk between the frames
with an iron plate on a pivot bolt and a lifting handle, the plate housed with
its head above the case. Modelled down it would have been a 0.9 m fin under a
boat that documents a 1 ft 5 in draught; drawn up, it is what you see in the
davits. This also forced the interference test to earn its keep: the trunk
cheeks have to clear the inside of the planking along the whole of their
length, not just at the widest frame.

**Clinker over nine strakes, finished in two schemes.** The bottom three
strakes are painted, the six above varnished elm — which is how a naval whaler
was actually finished, because the paint is the part that takes the beach. Each
varnished strake gets its own timber tone, the same trick as Boat B: at 1240 px
you read the plank count from the colour before you can resolve an 18 mm strake
standing proud of the 12 mm lap below it.

**A raked stem needed a different rudder setting-out.** The rudder hangs on the
counter post, which on this boat rakes aft as it rises *and* sits at the
minimum x, not the maximum: +X is forward. The first attempt placed the blade
by maximising x and buried it 140 mm inside the planking; the interference
check found 224 penetrations. Aft is now found by sampling the counter profile
for the smallest x at each height, the blade stands 55 mm clear of it, and the
assembly carries two pintles on the after face of the stem, a stock above the
sheer and a forward-reaching tiller for the coxswain.

**The standing-lug rig is stowed, not set.** Yard up and mast hoops on, sail
rolled down on top of the yard and stopped with rope gaskets, exactly as a boat
lying in davits carries it. A bare tapered spar reads as a scaffold pole; a
bundle of canvas with ropes round it reads as a sail that has been put away.
Boat C carries two masts to Boat B's one, so the stowed sails are also what
keep the rig from looking like two sticks.

**Thwart knees.** Four thwarts, each landing on a pair of grown knees against
the planking rather than on a timber shelf. The knees are the detail that makes
an open boat read as built rather than assembled: nothing in the interior meets
at a right angle.

## Third pass — what the containment test found

The interference tests compare named pairs: propeller against hull, rudder
against planking. They are blind to the thing that actually ruins a small-boat
render, which is a piece of gear standing ten millimetres out through the
outside of the planking and casting a hard shadow down a varnished topsides.

So `verify.py` now measures every vertex of every interior object against the
hull envelope, and the three boats between them had ten defects that no
interference test had ever looked for:

* **A's engine bearers** were a square 100 × 180 mm section standing in a bilge
  that is 0.44 m wide at its lower arris — 152 mm of starboard bearer out
  through the bottom planking, invisible under water and obvious the moment the
  model is cut. They are chamfered on the lower outboard arris now, following
  the bilge, which is what a bearer in a bilge is.
* **A's feed-water tank and coal bunker** were boxes sized for a boat-shaped
  hole. Both are sized from the bilge now.
* **A's cross floors** measured the breadth of the hull 160 mm up the topsides,
  where it is wider, and came out 69 mm too long.
* **A's deck edges** were laid to the breadth of the sheer measured 70 mm above
  the deck, and stood 39–55 mm outside the planking at the bow. A deck is only
  as wide as the boat is at the deck.
* **B's boat hook** — the second time this fitting has caused trouble — ran
  forward from a butt abreast the fore thwart, which put its head 589 mm out
  through the bow. It starts further aft now, and its offset is capped by the
  narrowest station it passes.
* **B's mast clamp** was cut to the breadth at the sheer, 70 mm above where it
  is bolted.
* **C's stowed oars** were the same mistake as the hook, five times over: a
  5.18 m oar lying fore-and-aft at a fixed offset from the centreline leaves the
  hull wherever it narrows. The blades were 205 mm outside the bow planking.
  Oars now lie on the thwarts with their offset computed from the narrowest
  station they cross, and they are where they belong — resting on the thwarts,
  not hanging in the topsides.
* **C's grapnel** was hung at a fixed offset near the after end, which on a
  double ender is a place where the hull is 0.21 m wide, so it floated in the
  air 340 mm outside the boat. It stands on the bottom boards forward of the
  centreboard case now, which is also where two men would want it.
* **C's thwart knees** were vertical slabs; a knee hanging 200 mm down a
  topsides that is falling away needs its outer face tapered to the planking.
* **C's frames and keelson** ran at full thickness into stems where the hull is
  6 mm wide, so both are sided down over the last 0.45 m at each end.

**Framing.** `frame_camera` fitted a bounding sphere, which on a boat with an
8.7 m box and a 5 m mast spends most of the frame on air. It solves the distance
from the projected corners of the box now: same arithmetic, tighter frame, and
nothing can be clipped because every corner is inside the frustum by
construction.

**Fenders are their own part.** A fender hanging plumb outside a hull that
curves away beneath it is meant to be outside the planking. Splitting it out of
`Fittings` lets the containment test hold every other piece of gear to the hull
without special cases, and the exports carry it as `gear` instead of dropping
it as an unknown part.

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

**Boiler furniture.** A vertical boiler is something you walk round and reach
over: it now carries a brass handrail on eight stanchions round the upper
shell, and a maker's plate with a raised bezel on the side a passenger would
see. Small things, but "manufactured object" cues like these are what separate
a modelled machine from a modelled cylinder.
