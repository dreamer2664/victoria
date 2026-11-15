# ASSET LICENCES

## Summary for a hurry

**No third-party 3D model, texture, HDR, font file or mesh is redistributed in this
repository.** Every mesh, every texture and every sign is generated from code in
`blender/lib/` at build time. The only third-party material committed is
public-domain book plates in `reference/plates/`, used as *documentation*, not as
scene content, and one system font that is only *read* at texture-generation time and
never redistributed.

This matters because the brief permits free models for buildings and architectural
assets, but forbids downloaded port environments or ships. In the event, **zero**
models were downloaded: the four candidate libraries surveyed did not contain 1889
British dock architecture at a usable standard, and the checks below record why.

---

## 1. Geometry — 100% authored in this repository

Every object in both ports is built by the Python mesh builders in `blender/lib/`:

| Module | Contents | Provenance |
|---|---|---|
| `core.py` | `MeshBuilder` primitives (box, cylinder, beam, gable/hip roof, prism, grid quad), constants, 51 materials | authored |
| `parts.py` | windows, doors, quoins, cornices, handrails, columns, roof-lights, chimneys, stairs | authored |
| `bldg.py` | warehouses, transit sheds, terminal, station, office blocks, terraces, shops, moulding loft | authored |
| `maritime.py` | quay walls, graving docks, caissons, slipways, landing stage, bollards, capstans, lighthouses | authored |
| `machinery.py` | cranes, winches, capstans, coal hoists, staithes, rail, wagons, locos, cargo stacks, plate stacks | authored |
| `signs.py` | painted signboards, fingerposts (baked to PNG) | authored |
| `proxy.py` | the 180 × 20 × 9 m clearance block-out — **not a ship asset** | authored |

No mesh in this repository is derived from, traced from, or retopologised from a
third-party model. There is therefore nothing to attribute and no licence to carry.

## 2. Textures — procedurally generated

`blender/lib/texgen.py` writes all 48 texture maps into `textures/` from NumPy noise
and geometry. Sixteen materials, each with an albedo / roughness / normal triple
(`*_alb.png`, `*_rgh.png`, `*_nrm.png`):

`brick_blue`, `brick_buff`, `brick_soot`, `canvas`, `coal`, `granite`, `iron`,
`plank`, `rubble`, `sandstone`, `setts`, `slate`, `steel_plate`, `stucco`,
`terracotta`, `timber`.

Regenerate with:

```bash
python3 blender/lib/texgen.py textures
```

Licence: same as this repository. No sampled photographs, no scanned textures, no
Poly Haven / ambientCG downloads.

## 3. Signs and lettering

`blender/lib/signs.py` bakes 23 signboards to `textures/signs/*.png` using
**DejaVu Serif Bold** and **DejaVu Sans Bold** from `/usr/share/fonts/truetype/dejavu/`.

- Font: DejaVu, based on Bitstream Vera. Licence: Bitstream Vera Fonts Copyright —
  permissive, allows redistribution and commercial use, requires that the font not be
  sold by itself. **The font file is not redistributed here**; it is only read at
  texture-generation time on the build machine. The generated PNGs are images, not
  fonts, and carry no font-licence obligation.
- All lettering content is fictional: `ALDERMOUTH HARBOUR BOARD`, `RAVENNA STEAMSHIP
  Co.`, `MERIDIAN LINE`, `ALBION & ATLANTIC STEAM NAVIGATION Co. Ltd.`,
  `MERRION SHIPBUILDING & ENGINEERING Co. Ltd.` and so on are invented names. No real
  company's marks, liveries or wordmarks are reproduced.

## 4. Reference plates — public domain

`reference/plates/` contains 18 plates copied from:

> J. R. Soley et al., *Ocean Steamships: A Popular Account of their Construction,
> Development, Management and Appliances*. New York: Charles Scribner's Sons, 1891.
> Retrieved as Project Gutenberg eBook **#54136**,
> <https://www.gutenberg.org/ebooks/54136>.

- **Status of the underlying work:** published 1891, therefore in the public domain in
  the United States and in all jurisdictions where the term is author's life + 70
  years (all contributors died before 1955). The images are reproductions of
  pre-1892 photographs and engravings.
- **Project Gutenberg's terms:** the *eBook text* is under the Project Gutenberg
  Licence, which requires removal of the "Project Gutenberg" trademark if you
  redistribute a modified version. What is redistributed here is (i) plates whose
  underlying works are PD and (ii) short quotations for scholarly citation. The
  Project Gutenberg header, footer and trademark are **not** reproduced, and no
  Project Gutenberg branding appears on `reference/reference_board.html`.
- **What they are used for:** annotation and provenance in the reference board only.
  **No plate is used as a texture, decal, billboard or in-scene image anywhere in
  either port.**

## 5. Models surveyed and rejected

The brief required inspecting any downloaded free model before use. The survey is
recorded here in full, including the negative result.

| Candidate | Result | Reason |
|---|---|---|
| Warehouse / factory kits (generic game-art packs) | rejected | modern roller shutters, steel portal frames, concrete plinths, no 1889 masonry vocabulary |
| "Old port" prop packs | rejected | pirate-adjacent dressing (rope coils, anchors, barrels as decoration, lanterns); the brief explicitly excludes pirate harbours |
| Victorian street packs | partially rejected | mostly London terraced shopfronts; only the bay rhythm was worth reading, and that was hand-authored instead in `bldg.office_block` |
| Prebuilt port environments / ships | **not downloaded at all** | prohibited by the brief; the waterfront, dock system and all maritime infrastructure were required to be hand-built, and are |

Consequence: **nothing needed to be integrated, modified or licence-cleared.** The
inspection requirement was satisfied by surveying and rejecting, and the resulting
assets are stronger for it — an imported warehouse would have had a different
construction vocabulary from everything beside it.

## 6. Exports

`assets/glb/` and `assets/fbx/` are generated from the `.blend` files by
`blender/build_ports.py`. They contain only geometry, materials and texture references
from this repository. The glTF exporter embeds the texture PNGs into the `.glb`.

## 7. Third-party code

| Component | Licence | Use |
|---|---|---|
| Blender 4.2.1 LTS | GPL-2.0-or-later | build tool — not redistributed, invoked as a subprocess |
| Python 3 `numpy`, `Pillow` | BSD-3 / HPND | texture and sign generation — not redistributed |
| `git` | GPL-2.0 | version control |

No GPL code is linked into or derived into the exported assets: the `.blend`, `.glb`
and `.fbx` files are data produced by a GPL program, which does not make them GPL.
