# qwen-image-2 skill

Claude Code skill for generating and editing images with Qwen-Image-2.0 (Alibaba) through
fal.ai or Alibaba Model Studio.

- `SKILL.md`: availability check, tier choice, 2K sizes, prompt rules for text-to-image and
  edits, Qwen settings for reference fidelity and anatomy, defect check.
- `references/api.md`: endpoints, fields, limits, sizes (fal, Model Studio, WaveSpeed).
- `references/prompt-patterns.md`: templates for posters, slides, infographics, comics,
  calendars, portraits, products and edit instructions.
- `references/observations.md`: dated test results.
- `scripts/qwen_payload.py`: builds and validates a fal payload (size, prompt limits, quotes,
  image references, preservation clause, alpha flattening).

The repository also carries a second, model-agnostic skill in `image-edit-fidelity/`:
anatomy, reference fidelity, part transfer, head swap and the `ref_diff.py` check for any
image model. `qwen-image-2` refers to it at `~/.claude/skills/image-edit-fidelity`.

Install:

```bash
git clone git@github.com:daniil-kzn/qwen-image-2-skill.git ~/.claude/skills/qwen-image-2
ln -s qwen-image-2/image-edit-fidelity ~/.claude/skills/image-edit-fidelity
```

Requires Python 3 with Pillow; execution goes through the `fal-runner` skill (`FAL_KEY`).
