---
name: tno-portrait-artist
description: Create, restore, colorize, composite, and strictly validate photographic The New Order (TNO) leader portraits for Hearts of Iron IV. Use for TNO 头美、人物头像、156×210 leader portraits, historical-photo restoration, identity-preserving uniform edits, cutouts, faction-style matching, or portrait contact-sheet review. Do not use for generic illustration or unrelated game art.
metadata:
  short-description: Create and validate photographic TNO leader portraits
---

# TNO Portrait Artist

Produce a portrait that looks like a restored historical photograph inside the requested TNO faction, not merely an image that passes numeric checks.

## Read only what the task needs

- Always read [references/style-standard.md](references/style-standard.md) before setting composition, color, texture, or acceptance targets.
- Read [references/imagegen-workflow.md](references/imagegen-workflow.md) when AI restoration, colorization, clothing replacement, or identity preservation is needed.
- For local files, prefer the deterministic helpers in `scripts/` over rewriting metric, contact-sheet, cutout, or compositing code.

## Non-negotiable invariants

1. Identity and source authenticity outrank style. Begin from a verified photograph whenever one exists; record uncertainty when the date is approximate.
2. Treat tutorials as process guidance and finished TNO portraits as the visual authority. Calibrate to the requested faction and comparable age, pose, occupation, and source quality.
3. Never change a user-supplied fixed background globally. A requested feather or contour shadow may affect only the narrow subject boundary; all other exposed background pixels must remain exact.
4. Keep face restoration, clothing replacement, background extraction, grading, and packaging as separate checkpoints. Preserve the last clean checkpoint before each risky edit.
5. Numeric ranges are rejection gates, not proof of style. A portrait that looks modern, painted, waxy, too small, too warm, or obviously generated still fails.
6. Do not create a DDS/texticon, character entry, sprite registration, or Git commit unless the request includes that deliverable or integration step.

## Workflow

### 1. Establish the source and target

- Verify identity from at least one credible page and prefer 3–6 historical photographs when available.
- Prefer the requested decade. If no precisely dated photograph exists, use the nearest plausible period without AI age regression and disclose the date uncertainty.
- Build a reference set in layers: broad TNO library, geographic/faction set, closest completed portraits, then 20–40 comparable people.
- If available locally, inspect the tutorial folder and recursively discover `gfx/leaders` rather than assuming a fixed workshop ID. Known personal locations are listed in the style reference.

### 2. Make a high-resolution identity anchor

- Work at no less than 312×420; use 1080×1456 or similar for restoration and cutout work.
- Restore scan damage, print screens, and missing tonal range conservatively. Preserve face proportions, hairline, ears, gaze, expression, age, asymmetry, and real skin structure.
- If the user requests different clothing, edit only clothing after the face anchor is accepted. Use explicit garment construction and ban text-like insignia.
- Inspect every generated result before continuing. Reject face drift, invented accessories, nonsensical insignia, baked checkerboards, modern studio polish, or painting texture.

### 3. Composite deterministically

- Verify whether the generated file truly has alpha. A visible checkerboard in an RGB image is opaque pixels, not transparency.
- Extract simple white/checker/chroma backgrounds with connected-background segmentation. Do not protect arbitrary lower-center regions that can preserve wedges.
- Use premultiplied-alpha resizing. Feather the edge at final size, add only the requested shallow contour shadow, and preserve the fixed background outside that band.
- Set scale and vertical position from measured face ratio and eye line; do not accept a half-body crop just because the hair-to-chin height looks plausible.
- Grade only the subject when the background is fixed. Shape facial planes with light and local contrast; never change jaw geometry to manufacture “angularity.”

### 4. Validate before integration

Run:

```powershell
python scripts/analyze_portrait.py <portrait.png> --preset dop-gng
python scripts/make_contact_sheet.py --output <board.png> <references...> <portrait.png>
```

Also inspect:

- the exact 156×210 image;
- a 4× nearest-neighbor enlargement;
- a labeled comparison board;
- a hidden/shuffled comparison board when strict matching is requested.

Fail and return to the last clean checkpoint if the candidate is immediately identifiable by warmth, brightness, small head, excessive clothing, halo, low resolution, or AI texture.

### 5. Package the requested deliverables

- Default leader output: `156×210`, RGBA PNG, fully opaque unless the consuming mod requires alpha.
- Keep a high-resolution master and source/provenance list when the user asks for process retention.
- Build a TNO texticon only when requested, using the actual target template and encoding; do not infer one faction's blue filter for unrelated portraits.
- Stage and commit only named files in a dirty worktree. Never use broad staging for portrait work.

## Restart conditions

Restart from the real photo or last clean master instead of patching when any of these occurs:

- identity, face shape, age, expression, or hairline drifts;
- the face is too low-resolution to retain eyes, mouth, wrinkles, and hair at 4×;
- clothing or insignia contains AI gibberish;
- repeated editing increases painting/wax texture;
- the cutout loses real neck, shoulder, hair, or ear structure;
- two edit rounds on the same generated branch do not converge.

## Completion standard

Do not call the task complete until the output passes the hard gates in the style reference and survives original-size, 4×, and mixed-board visual review. Report the final path, source/date uncertainty, whether built-in image generation was used, the final prompt focus, validation results, and any optional integration performed.
