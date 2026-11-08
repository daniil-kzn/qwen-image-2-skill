---
name: qwen-image-2
description: Generate and edit images with Qwen-Image-2.0 (Alibaba, Feb 2026; one model for text-to-image and editing, native 2K, strong Chinese/English text rendering) through fal.ai (`fal-ai/qwen-image-2/...`) or Alibaba Model Studio (`qwen-image-2.0`, `qwen-image-2.0-pro`). Covers the availability check, tier and endpoint choice, explicit 2K sizes, prompts written by the official Qwen rewriting rules, exact quoted text for posters/slides/infographics/comics/calendars, edit instructions with image 1/2/3 references, strict fidelity to attached references (inventory of people, objects and setting, change only what was asked, pixel diff against the reference, paste-back repair), prompt-expansion and negative-prompt settings, and a defect check before showing. Use whenever the user names Qwen for pictures ("сгенерируй в Qwen", "сделай постер через квен", "отредактируй фото в Qwen Image 2", "qwen image 2 pro", "квен 2"), or picks Qwen-Image for an image that must carry exact rendered text (poster, slide, infographic, menu, comic with speech bubbles), even if the user does not say "2.0".
---

# Qwen-Image-2.0

Qwen-Image-2.0 (released 2026-02-10) is one model for text-to-image and image editing: an
8B Qwen3-VL encoder plus a 7B diffusion decoder, native 2K output, instructions up to about
1k tokens. Its strengths are dense, correctly spelled text in Chinese and English (slides,
posters, infographics, comics, calendars, calligraphy), photorealism with low "AI look", and
multi-image edits. Officially supported prompt languages are Chinese and English.

Execution goes through `fal-runner` (journal, price, approval, download). Prompt craft for
video start frames stays in `storyboard-keyframes` / `kling-video-prompt`; this skill covers
Qwen-specific parameters and prompt rules. Dated test results live in
`references/observations.md`; API details, sizes and limits in `references/api.md`; ready
prompt templates in `references/prompt-patterns.md`.

## 0. Availability check (do it first in a new task)

fal marked all four `fal-ai/qwen-image-2/*` endpoints `deprecated` on 2026-08-18; the
successor `alibaba/qwen-image-3/*` is active. The standard text-to-image endpoint still served
a request on 2026-11-08, but deprecated endpoints may stop at any time. Before the first paid call of a task:

1. `python3 ~/.claude/skills/fal-runner/fal_run.py models qwen-image-2` and `schema <endpoint>`.
2. Check `references/observations.md` for the last successful run date.
3. If a call fails with 404/410/"deprecated"/"not found", report it to the user and offer the
   alternatives from `references/api.md` (Alibaba Model Studio needs `DASHSCOPE_API_KEY`, not
   configured on this machine as of 2026-11-08; WaveSpeed; or Qwen-Image-3 on fal as a
   different model that needs its own test). Never switch the model silently: the user asked
   for Qwen 2.

## 1. Tier and endpoint

| Task | fal endpoint | Price seen (2026-11-08) |
|------|--------------|-------------------------|
| Drafts, exploration, layout tries | `fal-ai/qwen-image-2/text-to-image` | 0.035 USD/image |
| Final image, dense text, realism | `fal-ai/qwen-image-2/pro/text-to-image` | 0.075 USD/image |
| Edit draft | `fal-ai/qwen-image-2/edit` | 0.035 USD/image |
| Final edit, multi-image fusion | `fal-ai/qwen-image-2/pro/edit` | 0.075 USD/image |

Model Studio names: `qwen-image-2.0` (accelerated) and `qwen-image-2.0-pro`, both serve
generation and editing on one endpoint (`references/api.md`). Iterate composition and text
on the standard tier, move to Pro once the prompt is settled, and compare the cost of the
accepted image including retries, not the price of one output.

## 2. Parameters that change the result

- **Size.** fal defaults to `square_hd` = 1024x1024, a quarter of the native 2K. Always pass
  `image_size: {"width": W, "height": H}`. Total pixels between 512x512 and 2048x2048, sides in
  multiples of 16. 2K presets: 1:1 2048x2048, 16:9 2688x1536, 9:16 1536x2688, 4:3 2368x1728,
  3:4 1728x2368, 3:2 2496x1664, 2:3 1664x2496. `scripts/qwen_payload.py size <ratio>` computes
  any other ratio. For edits without `image_size` the output follows the LAST input image.
- **Prompt expansion** (`enable_prompt_expansion` on fal, `prompt_extend` on Model Studio),
  default `true`: an LLM rewrites the prompt and adds details, style and camera words (the
  official example turned a one-line cat into a "Canon EOS R5, National Geographic" prompt).
  Default for this skill: write the full prompt yourself by the rules in §3/§4 and set it to
  `false` when the image carries exact text, a fixed layout, a series that must match, or a
  seed comparison. Keep `true` only for short exploratory prompts where variety is wanted.
- **Negative prompt**, at most 500 characters. Text-to-image default (the official Qwen list):
  `low resolution, low quality, deformed limbs, malformed fingers, oversaturated colors, waxy
  skin, faces without detail, over-smoothed, AI-generated look, chaotic composition, blurry or
  distorted text`. Edits: the fidelity list from §4a (the payload script's edit default;
  `--negative blank` sends `" "`), plus the failure you actually saw (`altered face`,
  `misspelled text`). Exclusions go here; the positive prompt does not list objects with "no".
- **Prompt length.** fal edit: 800 characters (schema). fal text-to-image: no limit in the
  schema; Model Studio truncates silently after 1300 tokens; WaveSpeed allows 800 characters.
  `qwen_payload.py` warns on the limits. When space runs out keep, in order: exact text strings,
  their positions, subjects and spatial relations, one or two style cues.
- **Count and seed.** `num_images` 1-4 (fal text-to-image), 1-6 (fal edit, Model Studio).
  `seed` 0..2147483647; the same seed gives similar, not identical, output.
- **Edit inputs.** 1-3 images, order = "image 1/2/3" in the prompt, 384-5000 px per side on fal
  (384-3072 recommended by Alibaba), at most 10 MB, PNG without alpha (the script flattens
  alpha). Local files go in as `"@file:/abs/path"` for `fal_run.py`.
- **Safety checker** is on by default; switching it off requires account authorization.

## 3. Text-to-image prompt rules

These follow the official Qwen rewriting system prompts (`prompt_utils.py`,
`prompt_utils_2512.py` in QwenLM/Qwen-Image) and the 2.0 launch examples. Writing the prompt
this way does the rewriter's job up front, which is why expansion can stay off.

1. Natural descriptive prose in one block, not keyword lists or tag soup. Structured content
   (infographics, tables, comics) may use line breaks and "Row 1: ..." sections, but each item
   is still a descriptive phrase.
2. Name the overall style explicitly: realistic photography, casual smartphone snapshot,
   movie poster, flat infographic, Song-dynasty gongbi painting, 3D render, anime illustration.
3. Order: subject, appearance, clothing head to shoes, pose, gaze and hands, other objects,
   environment, light (direction, intensity, color temperature), camera and composition,
   texture and mood. Restrain detail in simple scenes; add detail where it settles a real
   choice.
4. People: ethnicity, gender and a specific age ("about 30", not "young"); face shape, eyes,
   skin tone and texture, makeup; hair color, length, cut; every garment and accessory; body
   posture, gaze direction, what each hand does. About 200 words for a portrait. For realism,
   official examples use "casual iPhone snapshot, typical indoor lighting, no staged lighting".
5. Every visible string in double quotes, exactly as it must appear, with its position,
   orientation (horizontal, vertical, right-to-left columns), font (sans-serif, serif,
   handwritten, a named calligraphy style), color, size and carrier (neon tube, chalk, embossed
   gold foil, embroidery). Implied text becomes concrete text: not "a list of names" but the
   names. Close a text image with "No other text appears in the image."; a picture without
   text gets "The image contains no recognizable text."
6. Keep proper nouns, brands, slogans, URLs and numbers verbatim.
7. Layouts: describe the grid or columns first, then each block in reading order with its
   exact text; tables and calendars cell by cell; comics as "a 4x6 grid with white dividers",
   then "Row 1, panel 1: ... Speech bubble: \"...\"". Repeat a recurring character's short
   identity description word for word in every panel (the official comic does this) to keep
   them consistent. Pictures inside a slide go in parentheses next to their node.
8. Language: write the description in English or Chinese; keep quoted strings in the language
   they must appear in. Other scripts are not officially supported. Cyrillic tested
   2026-11-08: short common words often right, longer or rarer words garbled (2 of 3 Russian
   strings had wrong letters while English was exact). For Russian text: keep strings short,
   expect retries, check each word, and plan to fix wrong words in an editor or by an edit pass.
9. No quality-tag suffixes ("8K, masterpiece, ultra HD"): the 2.0 examples do not use them and
   they push toward the glossy AI look the negative prompt fights.

Templates for posters, slides, infographics, portraits, products, comics and calendars are in
`references/prompt-patterns.md`.

## 4. Edit instruction rules

From the official edit-prompt enhancer and the 2.0 edit examples:

- One direct, specific instruction: verb, target, attributes, position. "Add a light-gray cat
  in the bottom-right corner, sitting and facing the camera", not "add an animal".
- Replacement: "Replace Y with X", then X's key visual features.
- Text: `Replace "old text" with "new text"`, quotes kept, same language and capitalization;
  position, color and font only when they change.
- People: name what must stay (ethnicity, gender, age, face, hairstyle, expression, outfit).
  Expression and makeup changes subtle, never exaggerated.
- Style transfer: describe the target style by visible features (palette, line, texture,
  light), and put the style sentence after the content changes.
- Multi-image: say which image supplies what ("the girl from image 1 wears the black dress
  from image 2 and sits in the pose from image 3"), which image gives the background, and
  describe each person's clothing and pose. The output aspect follows the last image: put the
  base image last or set `image_size`.
- Preservation clause naming concrete things: "Do not change the real buildings, streets,
  vehicles or people; keep the photo realistic", "keep the product shape, logo and layout
  unchanged". With an attached reference always follow §4a.
- The model re-renders the whole frame. Compare unchanged areas side by side with the input;
  when a small local edit damaged the rest, paste only the edited region back onto the
  original with a feathered mask (same method as `storyboard-keyframes`).
- Colorization template: "Restore and colorize the photo." Inpaint/outpaint templates from the
  Qwen-Image-Edit enhancer ("Perform inpainting on this image. The original caption is: ...",
  "Extend the image beyond its boundaries using outpainting. The original caption is: ...")
  are not yet verified on 2.0.

## 4a. Reference fidelity: change only what was asked

Whenever the user attaches a reference image, the reference is the ground truth and the
request is a minimal diff on top of it. Everything the user did not ask to change stays as it
is: number of people and who they are, their poses and places, clothing, the room or street,
furniture and objects around, their count and positions, framing and camera angle, light
direction and color, style and texture, any text. An edit that "looks good" but added a
person, moved a chair or changed the window is a failed edit. The model re-renders the whole
frame and is free to "improve" it, so fidelity has to be asked for explicitly and then checked.

1. **Inventory the reference before writing anything.** Look at it at full size (crops for
   small areas) and write `reference_inventory.md` in the project folder:
   - framing: shot size, camera height and angle, what touches each frame edge, aspect, pixels;
   - people: exact count; for each, position in the frame (left/center/right, foreground or
     background), pose, gaze, hands, clothing head to shoes, hair, age, what they hold;
   - setting: room or place, walls, windows, doors, floor, furniture with positions;
   - objects: every visible item with count, color and where it lies (3 cups on the table,
     not "cups");
   - light: source direction, hardness, color temperature, shadows, time of day;
   - style: photo or illustration, grain, color grading, depth of field;
   - text and logos, verbatim.
   Then split it into two lists: `CHANGE` (only what the user asked) and `KEEP` (all the rest).
   If the request is ambiguous about scope ("make it cosier": furniture? light? both?), ask
   before generating instead of letting the model decide.
2. **Write the edit prompt as change + keep.** First sentence: the requested change, specific
   and local (what, where, how big, which side of the frame). Then the preservation clause
   built from `KEEP`, naming concrete items rather than "everything else": "Keep exactly two
   people: the man on the left in a grey sweater and the woman on the right in a blue dress,
   same faces, poses and positions. Keep the wooden table with three white cups, the window on
   the left, the bookshelf on the right, the warm light from the window, the framing and the
   camera angle unchanged. Do not add or remove any people or objects." Under the 800-character
   edit limit, keep the items most likely to drift: people count and identity, objects near
   the edited area, background architecture, framing. Describe only the change in detail; do
   not re-describe the whole scene in new words, which invites the model to redraw it.
3. **Settings that protect the reference:**
   - `enable_prompt_expansion: false`: the rewriter adds details, props and style words that
     are not in the reference.
   - Output size = the reference's aspect and size (the payload script does this by default
     for edits); a different aspect forces the model to invent or crop content.
   - The base reference goes LAST in `image_urls` (output aspect follows the last image) and
     is called by its number in the prompt; attach only references that the change needs,
     each extra image is another source of drift.
   - Negative prompt for edits: `extra people, missing people, different person, changed
     background, added objects, removed objects, different framing, different lighting`.
   - Standard tier for drafts; one output per call until the instruction holds, then 2-3.
4. **Check against the reference, not on its own.** Run
   `scripts/ref_diff.py <reference> <output> --allow x0,y0,x1,y1` (the box where the change was
   supposed to happen, in reference pixels). It reports how much changed outside that box per
   grid cell and writes a side-by-side and a heat map. Then go through `reference_inventory.md`
   line by line on the output: people count and identity, each object and its position,
   background, light, framing, text. Any `KEEP` item that changed is a defect, even a small one.
5. **Repair instead of regenerating the whole frame.** When the change is right but the rest
   drifted, paste only the changed region back onto the original:
   `scripts/ref_diff.py <reference> <output> --allow <box> --paste-back final.png` (feathered
   edge, the rest of the frame comes from the reference pixel for pixel). If the change itself
   is wrong, tighten the `CHANGE` sentence and add the drifted items to `KEEP` by name; change
   one thing per retry.
6. **Report** to the user what changed and confirm what was verified as kept; name any
   accepted deviation.

## 5. Workflow

1. Ask only what changes the image: purpose and aspect ratio, the exact text strings and their
   language, photo or illustration, reference images. Otherwise take the defaults above.
2. Availability and schema check (§0), choose the tier (§1). With a reference image: write
   `reference_inventory.md` with the CHANGE/KEEP split first (§4a).
3. Write the prompt into the project folder (`prompt.txt`) and build the payload:
   `python3 ~/.claude/skills/qwen-image-2/scripts/qwen_payload.py build --endpoint <id>
   --prompt-file prompt.txt --ratio 16:9 --expansion off -o payload.json` (edits: add
   `--image a.png --image b.png`). Fix every warning it prints.
4. Quote model, number of images, size and price and wait for approval (fal-runner rules).
5. `fal_run.py submit <endpoint> payload.json --label "<what>" --wait`.
6. Check every output at full size before showing (§6).
7. Show the result the way the user reviews media: an HTML page with labelled `<img>` tiles in
   the built-in browser pane (global instructions), `naturalWidth > 0` verified, not
   `SendUserFile`. Copy finals out of `~/.cache/fal-jobs/` with descriptive names.
8. Iterate by changing one thing per round. Record new findings with a date in
   `references/observations.md` (failures stay listed).

## 6. Defect check

- Every quoted string character by character at full size (crop and zoom small text with PIL):
  spelling, digits, dates, punctuation, line breaks; no invented extra text, no duplicates.
- Layout: row and column counts, cell order, alignment, nothing cut by the frame edge.
- People and objects: counts, hands and fingers, gaze targets, anatomy, who stands where.
- Edits: `ref_diff.py` against the reference, then every line of `reference_inventory.md`
  (people count and identity, objects and positions, background, light, framing, text); output
  pixel size and aspect equal to the reference.
- Look: waxy or over-smoothed skin, oversaturation, wrong style drift from expansion.
- Returned size equals the requested size (fal falls back to 1024x1024 when `image_size` is
  omitted).
- Background signage and small print the prompt did not ask for come out as pseudo-text: keep
  them blurred or out of frame, or name their exact text.

Regenerate only images with real defects; report the defects you accepted.
