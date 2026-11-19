# Applied one-off micro-part corrections — do not rerun

`fix_micro_parts.py` through `fix_micro_parts_9.py` have ALREADY BEEN APPLIED.
These exact-match patchers are retained only as change evidence; they are not
part of the reproducible build. Re-running one can fail or duplicate work.
`_4` and `_5` failed an exact-match assertion before their final successful
applications; corrected versions are retained here. `_5` did not write the
machinery source on its failed attempt.

Subsequent direct source changes are recorded in
`docs/leonidas_ii/MICRO_DETAIL_REVIEW.json` and the actual generator sources.
They include flatware/napkin clearances, WC collar and piano hinge placement,
real rear-seat and bed spindle rails, tub mounting ears, and four-corner GAME
torus sections preserving inner radius and vertical extrema.

The ordinary `tools/build_leonidas_ii.sh` rebuilds from those final generators;
it must never invoke these patches. Isolated recipe/regression results do not
approve every assembled ship part or the delivered model.
