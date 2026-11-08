# image-edit-fidelity skill

Model-agnostic Claude Code skill for generating and editing images of people and scenes with
any image model (Qwen-Image, Nano Banana, GPT Image, Seedream, Flux Kontext, Kling and others).

- `SKILL.md`: intact human anatomy, strict fidelity to attached references (change only what
  was asked), transfer of exactly one part between references, head swap, defect check, how to
  express the rules for models with and without a negative prompt field.
- `references/edit-patterns.md`: ready edit instructions (KEEP clause, part transfer, head
  swap, object transfer, hand fix, several people) and exclusion lists.
- `scripts/ref_diff.py`: compares an edit with its reference outside the allowed area and
  pastes only the edited region back onto the original.

Model-specific skills (for example `qwen-image-2`) supply endpoints and parameters and refer
to this skill for the shared rules. Requires Python 3 with Pillow.

Lives in the `qwen-image-2-skill` repository; install it as a top-level skill with
`ln -s qwen-image-2/image-edit-fidelity ~/.claude/skills/image-edit-fidelity`.
