# TNO portrait skill test handoff

Installed skill: `tno-portrait-artist`

Installed location: `C:\Users\lizih\.codex\skills\tno-portrait-artist`

## New-session smoke test

Open a new Codex task in this project and ask:

> 使用 $tno-portrait-artist 复查 `gfx/leaders/YUN/DOP_Long_Shengwu.png`，只报告是否通过 DOP/GNG 门禁和还需人工检查的项目，不要修改文件。

Expected behavior:

- the skill loads `references/style-standard.md`;
- it runs the installed `scripts/analyze_portrait.py` with `--preset dop-gng`;
- it reports a numeric pass while explicitly retaining original-size, 4×, and mixed-board visual review;
- it does not create a DDS, change files, or commit to Git.

## Validation already completed

- `quick_validate.py` passed on the build and installed directories;
- all three Python scripts passed compilation;
- analysis ran against the final Long Shengwu portrait;
- contact-sheet generation ran against three project portraits;
- deterministic extraction/compositing ran against the high-resolution Long Shengwu candidate and exact fixed background;
- the initial 54.76% face ratio was correctly rejected; a 55.24% revision passed.

This handoff file is not part of the skill and should remain uncommitted unless the user explicitly wants project documentation.
