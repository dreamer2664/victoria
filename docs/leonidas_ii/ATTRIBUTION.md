# Attribution and redistribution boundaries

## New deliverable assets

The LEONIDAS-II procedural geometry, Blender modules, scripts, original atlas artwork, compartment signs, analytical drawings and actual-model renders were authored for this reconstruction. No downloaded photograph is mapped onto the ship, passed off as new geometry, or used to conceal an empty compartment. No image-generation service was used for the model evidence. Historical comparators do not make the fictional ship an authenticated historical reconstruction.

The six `reference/leonidas_ii/materials/Aurelian_*.png` maps are original procedural images produced by `tools/leonidas_materials.py`. Sign lettering is rasterised with DejaVu Serif where installed; no standalone font file is redistributed. The source SVG sheets use ordinary system text, and the Cairo-produced PDFs contain embedded DejaVu Sans font subsets. The applicable copyright/trademark and permission notice is retained in [FONT_NOTICE.txt](FONT_NOTICE.txt). The kit's packed metal/roughness image derives from these same original maps.

This document does not relicense the repository or claim ownership of historical/museum images. The base repository has no project-wide licence file; recipients must establish their intended code/art redistribution terms separately. Existing third-party attributions are retained.

## Historical material actually used

| Material | Credit / locator | Use and redistribution note |
|---|---|---|
| Seven new period engravings/photographs: `i_040_a`, `i_040_b`, `i_041`, `i_087`, `i_099`, `i_102`, `i_103` | F. E. Chadwick and contributors, *Ocean Steamships*, Charles Scribner's Sons, New York, **1891**; [Gutenberg 54136 via Waterloo mirror](https://mirror.csclub.uwaterloo.ca/gutenberg/5/4/1/3/54136/54136-h/54136-h.htm), `images/<filename>.jpg` | Historical construction and mechanical relationships, not traced Aurelian plans. Gutenberg identifies the book as public domain in the United States; users outside the US should check local rules. Modern website presentation is not copied. Captions and exact interpretation are in DESIGN_AND_SOURCES.md. |
| Vertical marine engine model, MC.310578 / nmah_846155 | National Museum of American History, Smithsonian Institution; [object record](https://www.si.edu/object/model-vertical-marine-steam-engines:nmah_846155); image NMAH-AHB2016q019120 | Photo was opened for mechanical comparison. Record identifies **metadata** as CC0 but its accessible media panel also says usage restrictions apply. **Do not infer unrestricted media rights from metadata CC0.** The local research JPEG is excluded from the Git publication; the branch supplies the object/image links, not a newly licensed museum photograph. No image is in the game materials or import kit. |
| RMG NPC9465 (1880 launch), STD0019 (1895 launch) | Royal Museums Greenwich, [NPC9465](https://www.rmg.co.uk/collections/objects/rmgc-object-1182149), [STD0019](https://www.rmg.co.uk/collections/objects/rmgc-object-532343) | Catalogue metadata only; the actual sheets were unavailable. No sheet is reproduced and no visual/tracing claim is made. Launch plans are not liner evidence. |
| RMG SLR0772 / SLR1818 / SLR0719 model photographs | Six inherited photos on the inspected `agent/boats` tip, credited there under `refs/rmg/` | Actually opened for small-craft construction/interface understanding. Not copied into the new ship assets. Original branch ownership and terms remain unchanged. |
| Twelve inherited liner/interior plates | `reference/plates/`, inherited `reference/reference_index.json` | Visually reviewed; retained unchanged at the base commit. The older index's broad “PD” descriptions have not been independently cleared for every image here. They are not new material-map assets or historical dimensional authority. |
| Teutonic account and interior reproductions | *Ocean: A Magazine of Travel*, Vol. III No. 2, September **1889**, reproduced at [GGArchives](https://www.ggarchives.com/OT/Ships/Teutonic.html) | Period article informs joinery, furniture and incandescent lighting. Later Marconi/cabin-list material on the same page is excluded from the 1889 design. Modern site text/layout/media are not redistributed as original work. |

Full source register, accessed-evidence distinctions, comparator dates and design inferences: [DESIGN_AND_SOURCES.md](DESIGN_AND_SOURCES.md). Research access date used in the project register: 16 November 2026.

## Runtime and build dependencies

* Blender 4.2.3 LTS, Python/NumPy/Pillow: build dependencies, not bundled executable copies in the Git delivery.
* Intel Open Image Denoise 2, supplied with the local Blender installation: conventional denoising of actual Cycles pixels. No scene content is synthesized. Per-image processing and hashes are in the evidence register. Raw frames are regenerable scratch.
* CairoSVG/Cairo: optional SVG-to-vector-PDF conversion. The editable SVG files do not require it for editing.
* Luau **0.747**: parser and fake-API runtime logic tests. The Luau binary is not part of the game or branch.
* Khronos **glTF-Validator** npm package: format checks on the actual regional GLBs. It is not Roblox Studio certification.
* Roblox built-in smoke particle resource `rbxasset://textures/particles/smoke_main.dds`: referenced by the client, not downloaded/relicensed media. No copyrighted bell, whistle, engine recording, external sound ID, credential or token is bundled. Optional whistle audio must be uploaded and authorised by the experience owner.

## Branch ownership

No boat, port or QA branch asset is rewritten or merged. Compatibility records name the exact inspected tips and explicitly remain unilateral until their owners perform a joint integration test. Original historical claims and geometry remain recoverable from base commit `75bf4ac5770b803919b36c8dbdb5374df82d88ac`.
