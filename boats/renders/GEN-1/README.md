# GEN-1 — sequential boat render audit

**WORK IN PROGRESS: 9 of 45 images accepted. This is a pushed engineering checkpoint, not the completed release.**

This generation is being rebuilt and inspected one render at a time by THEMISTOCLES-III and THEMISTOCLES-IV. The historic `../them2/` batch was rejected and is not reused. Diagnostic renders are kept outside the release directory. See [AUDIT_LEDGER.md](AUDIT_LEDGER.md) for concrete per-image findings and fixes.

## Output contract

- Exactly 45 individually reviewed PNGs at 960 × 600 on completion: 15 each for the 25 ft rowing cutter, 27 ft whaler and c.1888 steam cutter.
- Current accepted images use CPU Cycles, 64 samples with adaptive sampling and denoising; AgX Medium High Contrast.
- Dry views use a seamless studio cove and real keel blocks; afloat views use the solved loaded waterline at Z=0, sky and sun, without studio lamps.
- Moving parts remain separate with documented pivots; every exported Roblox part must be at most 19,000 triangles. Final exports and `verify2.py` are still pending.
- Models have **not been play-tested in Roblox Studio**.
- Future releases are `GEN-2`, `GEN-3`, etc.; this directory is `GEN-1`.

## Current source corrections

Canted clinker laps; transom fitted to its rake and bevelled to the planking; keelson and frame sweep bases; correctly athwartship thwarts, knees and risers; sole boards supported on the floors; in-hull oar/spar stowage; 10 ft hooks on the thwarts; loose gear landed on the boards; painter on the starboard bow sheet; stem-rabbet breasthook and tapered cap-rail/inwale/rubbing-strake scarfs that meet the stem; hard timber edges preserved in shading; aimed off-axis studio lamps and true centreline end-on cameras.
