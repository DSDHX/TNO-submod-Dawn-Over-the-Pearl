# Identity-preserving image-generation workflow

Read this reference only when the portrait needs AI restoration, colorization, missing-detail repair, or clothing replacement.

## Roles and branch discipline

Label every input image:

- **Edit target:** the real person or accepted identity anchor.
- **Style reference:** palette, texture, composition, or clothing only.
- **Compositing input:** fixed background or separate garment/object.

Use the built-in image-generation tool by default. Load local edit targets into visual context first or use supported local-path editing when available.

Never feed a second portrait containing another visible face as a clothing reference unless the tool supports an explicit mask that excludes the face. Face-bearing style references can leak glasses, jaw, hairline, age, and expression into the target. Prefer a clothing-only crop or a text specification.

Keep separate checkpoints:

1. real scan;
2. restored/colorized identity anchor;
3. clothing edit;
4. deterministic cutout/composite;
5. final grade.

Do not edit the same generated branch more than twice. If identity or texture worsens, return to the last clean checkpoint.

## Restoration prompt template

```text
Use case: identity-preserve
Asset type: high-resolution master for a 156×210 TNO leader portrait
Input images: Image 1 is the real historical photograph and sole identity/edit target.
Primary request: conservatively restore and, if requested, colorize this exact photograph. Remove scan damage and print-screen interference; reconstruct only information lost to the scan.
Identity invariants: preserve exact skull, jaw, hairline, hairstyle, ears, eye shape/spacing, nose, mouth, expression, age, gaze, pose, and asymmetry.
Clothing invariants: preserve the existing clothing unless the user explicitly requested replacement.
Style: authentic restored archival photograph with pores, age lines, individual hair, fabric texture, and restrained grain.
Lighting/color: directional facial modeling, muted historical color, neutral-to-slightly-cool skin, no modern studio polish.
Avoid: beautification, symmetry correction, face reshaping, invented wrinkles, wax skin, painting texture, oversharpening, white rim, text, watermark.
```

Do not ask the model to make the image “more TNO” without the photographic constraints above. That phrase often produces illustration, exaggerated contrast, or fake old-photo effects.

## Clothing-edit prompt template

Use only after the identity anchor is accepted.

```text
Use case: identity-preserve
Input images: Image 1 is the sole edit target.
Primary request: change only the garment below the neck to <specific garment>.
Absolute face lock: preserve every facial feature, head shape, hair, ears, expression, age, gaze, skin texture, lighting, pose, head scale, crop, and background exactly.
Garment construction: <collar, fabric, shoulder structure, buttons, pockets, period, color>.
Insignia rule: use only large, simple, symmetric geometric marks; no letters, numbers, crests, ideograms, or tiny ornament unless a verified close reference is supplied.
Avoid: wrong garment class, costume gloss, brocade, modern camouflage, face drift, glasses, hat, medals, text, watermark, AI gibberish.
```

For an unmistakable historical officer tunic, specify fabric and construction instead of merely saying “military uniform.” Useful cues include tightly woven matte gabardine, structured stand collar, shoulder epaulettes, brass buttons, military seams, and restrained collar tabs. Explicitly ban overcoat, civilian Zhongshan suit, robe, and ceremonial costume when those are likely failure modes.

## Composition prompt guidance

Generation should leave enough pixels for deterministic reframing. Request:

- vertical head-and-shoulders portrait;
- hair-to-chin near 68% of the master height;
- both ears and hair top preserved;
- clothing limited to roughly the lower quarter;
- no hands, props, cap, or extra body unless requested.

Do not trust generation alone to hit final proportions. Measure and transform after the identity anchor is accepted.

## Output inspection

Immediately check:

- actual file mode and alpha extrema;
- whether a displayed checkerboard is baked into RGB;
- identity against the real source at the same crop;
- eyes, mouth, nose, ears, hair, collar, buttons, and insignia at 4×;
- modern retouching, false pores, repeated texture, or overly perfect symmetry.

Reject rather than repair when the face is wrong. Deterministic grading can fix brightness, saturation, crop, feather, and modest facial-plane lighting; it cannot reliably restore a drifted identity.

## Deterministic follow-up

After image generation:

1. extract the subject with true alpha or connected-background segmentation;
2. resize with premultiplied alpha;
3. set scale and vertical position from face/eye measurements;
4. composite over the fixed background;
5. grade the subject only;
6. add edge feather and optional shallow contour shadow;
7. use low-amplitude luminance-only dodge/burn for facial planes when needed;
8. run metrics and mixed-board review.

When a face lacks angular definition, restore cheekbone, nose-side, eye-socket, and jaw/neck separation through broad light and local contrast. Do not sharpen eyes and lips into black outlines or alter the jaw silhouette.
