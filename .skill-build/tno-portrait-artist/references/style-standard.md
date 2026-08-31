# TNO photographic portrait standard

Use this reference to choose visual targets and reject weak candidates. Finished portraits remain the authority; the numbers below prevent obvious drift but do not define style by themselves.

## Contents

- Reference hierarchy
- Known local reference locations
- Composition gates
- DOP/GNG color and tone baseline
- Texture and edge treatment
- Hard-fail defects
- Scoring and mixed-board acceptance
- Optional texticon packaging

## Reference hierarchy

Build the target from the top down:

1. **Requested output and user-approved portraits.** A fixed user-supplied background or approved faction set overrides generic TNO averages.
2. **Finished portraits from the same faction/route.** Compare original pixels and 4× enlargements.
3. **Regional portraits with similar age, pose, occupation, and source quality.** Use them for clothing, lighting, and restoration texture, not to copy faces.
4. **Broad TNO library statistics.** Use percentiles to catch outliers.
5. **Tutorials.** Use them for restoration and compositing methods; do not let a tutorial palette overrule finished in-game art.

Never calibrate one faction's brightness from another faction solely because the clothing is similar. In the DOP project, Yunnan portraits can inform military clothing and period cues, but the user-approved Guangdong portraits are the brightness, color, and texture anchor.

## Known local reference locations

Discover paths before relying on them. These personal defaults may exist:

- Tutorial folder: `D:\Steam\steamapps\workshop\content\394360\3473772709\TNO\图片类-头像美工`
- TNO portrait tree: recursively find `gfx/leaders` under Steam workshop item `2438003901` or the active TNO install.
- DOP approved Guangdong set: `<repo>\gfx\leaders\GNG\DOP_*.png`
- DOP fixed background when present: `<repo>\output\imagegen\sources\tno_portrait_background-source.png`

Useful tutorial files include the TNO palette/reference cards, computer workflow pages, and portrait-restoration guide. Inspect them visually; use OCR only when exact text is required.

## Composition gates

Default TNO leader output is `156×210` RGBA. Use at least `312×420` for the working master.

Target ranges:

| Measure | Target |
|---|---:|
| Hair top | 5%–12% of canvas height |
| Haar face-box height | 55%–60% of canvas height |
| Hair top to chin | 65%–72% of canvas height |
| Eye line | 38%–47% of canvas height |
| Clothing/shoulder area | bottom 20%–25% |

Interpret detectors cautiously. A detector box excludes hair and may vary with glasses or profile angles. It is still a hard warning when the face box is near 40%–45% and the mixed board shows excess torso.

When correcting composition, scale around the portrait center and shift the subject down enough to retain 5%–12% headroom and place the eyes correctly. Do not merely crop the top of the hair.

## DOP/GNG color and tone baseline

The following ranges come from the four user-approved DOP Guangdong portraits for Yeung Kwong, Yamashita Toshihiko, Niwa Uichiro, and Fok Ying Tung. Use them only for DOP/GNG matching or when the user explicitly chooses this baseline.

| Metric | Observed range | Practical gate |
|---|---:|---:|
| Global luma mean | 110.08–125.76 | 108–128 |
| Global saturation | 22.17%–26.71% | 20%–27% |
| P95 minus P5 contrast | 204.42–214.12 | 200–216 |
| Shadow pixels (`Y < 64`) | 24.09%–32.27% | 22%–34% |
| Highlight pixels (`Y > 210`) | 10.53%–14.12% | 9%–17% |
| Sharpness proxy | 466.54–709.27 | 440–730 |
| Skin luma | 123.27–142.05 | 120–145 |
| Skin red-minus-blue | 46.06–53.99 | 44–55 |
| Skin saturation | 31.25%–33.86% | 29%–35% |
| Background top-corner luma | 210.33–212.78 | reference only |

If the user supplies an exact background with different brightness, preserve it. Grade only the subject and judge the combined portrait visually; do not force the background into the table.

Use luminance-preserving saturation changes where possible. Do not lower global saturation by turning skin gray while leaving bright red insignia untouched. Check skin and uniform separately.

Contrast must describe useful facial planes, not black outlines around eyes and lips. Prefer cheekbone, eye-socket, nose-side, and jaw/neck separation. Preserve the person's real face geometry.

## Texture and edge treatment

Desired texture:

- real pores, age lines, hair strands, fabric weave, and restrained archival grain;
- slight old-photo softness without painterly smearing;
- no high-frequency sharpening rim or modern HDR clarity;
- no wax skin, beauty retouching, symmetrical face correction, or generated pseudo-wrinkles.

Cutout requirements:

- retain real hair, ears, neck, collar, and shoulder mass;
- no white wedge, chroma spill, baked checker square, or missing shoulder corner;
- use premultiplied-alpha resize to avoid bright fringes;
- a normal final feather is about 0.5–0.8 px;
- if requested, add a shallow, near-zero-offset contour shadow confined to roughly 2–3 px around the subject;
- outside the subject and explicit shadow band, a fixed background must be pixel-identical.

The contour shadow should read as separation, not a glow, sticker outline, or photographic drop shadow.

## Hard-fail defects

Reject regardless of metrics when any of these is visible:

- face or age drift from the real source;
- eyes, nose, lips, ears, or hair reduced to low-resolution generated blobs;
- painted, waxy, airbrushed, or modern corporate-headshot texture;
- clothing that reads as the wrong garment class;
- invented letters, numbers, crests, or illegible rank insignia;
- too much torso, immediate small-head appearance, or cropped hair;
- over-warm orange skin, flat frontal light, or pale face over a black body;
- halo, white fringe, missing neck/shoulder, hard pasted edge, or fogged background;
- visible checkerboard baked into RGB pixels.

## Scoring and mixed-board acceptance

Use a 100-point review:

| Category | Points |
|---|---:|
| Identity and source authenticity | 30 |
| TNO composition | 20 |
| Color, background, and light | 25 |
| Photographic texture/non-painting quality | 15 |
| Packaging and in-game display | 10 |

Require at least 90 points and no hard-fail defect.

Perform all three visual checks:

1. **Original size:** eyes, mouth, hair, collar, silhouette, and tonal balance must read at 156×210.
2. **4× nearest-neighbor:** inspect face regeneration, halos, checker remnants, sharpening rims, and insignia.
3. **Mixed board:** insert the candidate among 20–40 relevant portraits. Hide or shuffle names for strict review. If it is immediately identifiable by warmth, brightness, modern polish, small head, or painting texture, reject it.

## Optional texticon packaging

Do this only when requested.

- Inspect the actual faction template, dimensions, border, alpha, DDS encoding, and any color/blur layer.
- Replace only the portrait aperture. Preserve border pixels and encoding.
- Analyze an existing filtered and unfiltered pair; do not assume every TNO texticon uses the Guangdong blue treatment.
- Validate sprite registration, path, dimensions, alpha, and in-game tooltip display.
