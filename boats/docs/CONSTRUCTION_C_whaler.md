# Boat C — 27 ft double-ended whaler (c. 1890)

The third boat in the outfit, and the one that is not like the other two.

Both cutters have transoms and both are boats for carrying people about a
harbour. A whaler is a sea boat: pointed at *both* ends, clinker built, with a
drop keel and a two-masted standing-lug rig so she can be sailed as well as
pulled. The double end is not styling. The type grew out of the commercial
whaleboat, where you have to be able to back off a fish without turning the
boat — and it survived into naval service for a century because a boat that
can be rowed astern cleanly is a better sea boat in every other way too.

## Documented

| Item | Figure | Source |
|---|---|---|
| Length overall | 27 ft (8.230 m) | RN whaler type |
| Beam | 6 ft (1.829 m) | RN whaler type |
| Draught | 1 ft 5 in (0.432 m), plate up | RN whaler type |
| Normal load | 20.5 cwt (1021 kg) | RN whaler type |
| Capacity | 27 persons | RN whaler type |
| Construction | clinker (lapstrake), wych elm | RN whaler type |
| Ends | double ended — no transom | RN whaler type; "the 27 ft whaler was the only RN boat without a transom" |
| Oars | five, single banked: three one side, two the other | RNZN Naval Whalers |
| Oar lengths | 17 ft, bowman's 16 ft | RNZN Naval Whalers |
| Mainmast | 16 ft 6 in (5.03 m) | RNZN Naval Whalers |
| Mizzen | 13 ft (3.96 m) | RNZN Naval Whalers |
| Yard | 15 ft 3 in (4.65 m) | RNZN Naval Whalers |
| Rig | standing lug yawl | RN whaler type |
| Keel | drop keel (centreboard) | RN whaler type |

## Modelled

* **Hull.** `HullDesign` from `specs.WHALER`, nine clinker strakes on sixty-eight
  frames. Fine at both ends — the half-breadth runs from 28 mm at the stem to
  0.914 m at the fullest section and back to 28 mm at the after stem, which is
  what makes it a double-ender rather than a transom boat with a pointed bow.
* **Two stems.** A whaler has a stem at each end: the model carries a
  stem-shaped timber forward and a counter-stem aft, with deadwood wedges
  between the sections at both ends where the planking cannot close.
* **Drop keel.** Trunk with two cheeks and a cap, an iron plate head standing
  out of it with a lifting handle, and a brass pivot bolt. The plate is drawn
  *up*, which is the condition the documented 1 ft 5 in draught refers to and
  the condition a boat is hoisted in.
* **Rig.** Mainmast and mizzen stepped on the keelson through mast steps, each
  with its yard hoisted below the head, mast hoops holding the yard to the
  mast, canvas furled and stopped along the yard, rope gaskets, shrouds, a
  forestay, a mizzen stay and halyards led to the mast feet. The sails are
  **stowed**, because a boat lying in the davits stows her canvas.
* **Oars.** Five, single banked exactly as the type was pulled: three from the
  port side, two from the starboard. The bowman's oar is a foot shorter.
* **Interior.** Four thwarts on knees, pulling benches either side of the
  centreboard trunk, stern sheets with the coxswain's bench, seven-slat
  gratings lifted clear of the planking.
* **Gear.** Hoisting eyes on the keelson clear of the trunk, painter and stern
  rings, boat hook lying forward on the thwarts, bailer, the grapnel standing on
  the bottom boards forward of the trunk, a coir fender each side.

  Gear is a separate object from the hull furniture on purpose: every wooden
  fitting here is measured against the planking by `verify.py` (see
  `TESTING.md` §1.5), and a fender is the one thing on the boat that is outside
  the hull by design.

## Reconciliation with the documented figures

The floating waterline is *solved* from the weight table rather than assumed:
`boatgen.hydro` integrates the modelled form and finds the waterline at which
it displaces the loaded weight, then the whole hull is shifted so that
waterline sits at Z = 0.

| | Documented | Modelled / solved |
|---|---|---|
| Light weight | 20.5 cwt = 1021 kg | 1007.5 kg (−1.3%) |
| Loaded draught | 1 ft 5 in = 0.432 m | 0.436 m (+4 mm) |
| Loaded displacement | — | 1487.5 kg (light + six men) |

The agreement is better than the input data deserves, and it is worth being
honest about why: the beam and length are documented, so the displaced volume
follows, and the weight table was itemised to the documented light weight. What
the agreement *does* show is that the form is not an arbitrary shape — it
floats where a whaler of those dimensions should.

## What is reconstructed

* **The lines.** No traceable Admiralty body plan was used. The form is drawn
  to the documented length, beam and draught with a whaler's characteristic
  fine ends and nearly straight sheer. It is a reconstruction of a *type*, not
  a copy of a particular boat.
* **Frame spacing and scantlings** are taken from the other two boats and from
  period practice, not from a whaler's scantling table.
* **The rig is representative.** Mast and yard lengths are documented; the
  standing rigging arrangement is a reasonable modern reading of a
  standing-lug yawl, not a measured rigging plan.
