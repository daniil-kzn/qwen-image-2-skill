---
name: image-edit-fidelity
description: Model-agnostic rules for generating and editing images of people and scenes with any image model (Qwen-Image, Nano Banana / Gemini Image, GPT Image, Seedream, Flux / Kontext, Kling O3 image, Midjourney, Stable Diffusion and newer ones). Covers intact human anatomy for every person (one head, two eyes, two arms, two legs, five fingers per hand, no limbs from the back or chest, no fused bodies), strict fidelity to attached references (inventory of people, objects and setting, change only what was asked, keep the count of people, the setting and the objects around), transfer of exactly one part from one reference into another (garment, object, head swap: only the head is replaced, nothing else), a pixel diff against the reference with paste-back repair (`ref_diff.py`), and a defect check before showing. Use whenever an image is generated or edited with any model and contains people or uses a reference image ("отредактируй фото", "замени голову", "перенеси куртку с первого фото на второе", "поменяй только фон", "сгенерируй картинку с людьми", "edit this photo", "swap the face", "put this object into that picture"), together with the model-specific skill if one exists (for example `qwen-image-2`).
---

# Image edit fidelity and anatomy (any model)

These rules apply to every image model. They describe what the result must be and how to
check it; the model-specific skill (`qwen-image-2`, `storyboard-keyframes`, `fal-runner` for
execution) supplies endpoints, parameters, limits and prompt style. When a model-specific
skill exists, follow both: its parameters, these fidelity rules. Ready edit instructions are
in `references/edit-patterns.md`.

How to express the rules for a given model:
- **Negative prompt field** (Qwen, Seedream, Stable Diffusion, Kling): put the anatomy and
  fidelity lists from §1 and §2 there.
- **No negative prompt field** (GPT Image, Nano Banana / Gemini, Flux Kontext and most
  instruction-edit models): write them as positive statements in the prompt ("each person has
  one head, two arms and two legs", "the room, furniture and objects stay exactly as they are")
  and one short exclusion sentence at the end ("Do not add or remove any people or objects").
  Do not paste a long "no X, no Y" list into the prompt: many models draw the named objects.
- **Prompt rewriting** (Qwen `enable_prompt_expansion`, Model Studio `prompt_extend`, "magic
  prompt" options): switch it off for edits; the rewriter adds props and style that are not in
  the reference.
- **Which input sets the output size** differs by model (Qwen: the last image; others: the
  first, or an explicit size field). Check the schema, and make the output take the base
  reference's aspect and size.
- **Length limits** differ (Qwen fal edit 800 characters). When the KEEP clause does not fit,
  keep the items most likely to drift (§2 step 2).

## 1. Human anatomy: always intact

Every person in every output has normal human anatomy: exactly one head, two eyes, one nose,
one mouth, two ears, one neck, two arms attached at the shoulders, two hands with five fingers
each, two legs attached at the hips, two feet. No extra or missing heads, limbs, hands or
fingers; no limbs growing from the back, chest, belly or another person; no fused bodies; no
joints bending the wrong way. This applies to text-to-image and edits, to background people
and to stylized images (cartoon, comic, painting) unless the user explicitly asks for a
non-human creature. An image with a broken body is a defect, however good the rest is.

Why it breaks: diffusion models lose track of whose limb is whose where bodies overlap
(hugging, holding hands, crowds, a person carrying a child), where hands are small or hidden,
and in complex poses. Prevent it in the prompt and catch it in the check.

1. **Prompt.** For each person say where each arm and hand is and what it does ("her right hand
   holds a cup at chest height, her left arm hangs relaxed at her side"), and where the legs are
   ("standing, weight on the left leg", "sitting with legs crossed"). Name the body count when
   there are several people ("exactly three people, each with one head, two arms and two
   legs"). Write natural anatomy into the style sentence: "anatomically correct human bodies,
   natural proportions". Describe contact precisely: whose hand rests on whose shoulder.
2. **Composition that keeps bodies readable.** Prefer poses where both hands are visible or
   clearly hidden (in pockets, behind the back, out of frame); avoid tangles of interlaced
   arms, people standing directly behind one another, and limbs cut ambiguously by the frame.
   More people means smaller bodies and more errors: keep the count as low as the request
   allows; in crowds keep background people small, simple and partly occluded by clear objects.
3. **Anatomy exclusion list** (negative prompt, or one positive sentence where there is no
   negative field): `extra limbs, extra arms, extra legs, extra hands, extra fingers, missing
   fingers, two heads, extra head, extra eyes, fused bodies, limbs from torso, deformed hands,
   malformed anatomy`.
4. **Edits.** Changing a pose, clothing or adding a person must not add or lose body parts: put
   "same anatomy: one head, two arms, two legs for each person" into the KEEP clause (§2).
   A pose edit is the highest-risk edit; check every person in the frame, not only the edited
   one.
5. **Check every person before showing** (crop and zoom each body to full size; small
   background figures included): count heads, eyes, arms, hands, legs, feet; count fingers on
   every visible hand; trace each limb to its shoulder or hip and confirm it belongs to the
   right body; look for limbs growing from the back, chest or neck, merged hands, a third leg
   between two people, twisted joints. Write the count per person into the check notes
   ("P1: 1 head, 2 arms, 2 hands 5+5, 2 legs: OK").
6. **Fix.** A small hand or finger error: an edit pass on a crop around that hand ("correct the
   left hand: five fingers, natural pose, holding the cup"), then paste the crop back
   (`ref_diff.py --paste-back`). An extra or missing limb or head: regenerate with a simpler
   pose, fewer overlaps and the limb description from step 1. Never show an image with a
   broken body as a finished result; if the user wants to see a draft anyway, name the defect.

## 2. Reference fidelity: change only what was asked

Whenever the user attaches a reference image, the reference is the ground truth and the
request is a minimal diff on top of it. Everything the user did not ask to change stays as it
is: number of people and who they are, their poses and places, clothing, the room or street,
furniture and objects around, their count and positions, framing and camera angle, light
direction and color, style and texture, any text. An edit that "looks good" but added a
person, moved a chair or changed the window is a failed edit. Most models re-render the whole
frame and are free to "improve" it, so fidelity has to be asked for explicitly and then checked.

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
   camera angle unchanged. Do not add or remove any people or objects." Under a length limit,
   keep the items most likely to drift: people count and identity, objects near the edited
   area, background architecture, framing. Describe only the change in detail; do not
   re-describe the whole scene in new words, which invites the model to redraw it.
3. **Settings that protect the reference:**
   - prompt rewriting off;
   - output size = the reference's aspect and size; a different aspect forces the model to
     invent or crop content;
   - the base reference in the position that sets the output size, called by its number in
     the prompt; attach only references that the change needs, each extra image is another
     source of drift;
   - mask or inpainting mode where the model offers one: mask only the area to change;
   - fidelity exclusion list: `extra people, missing people, different person, changed
     background, added objects, removed objects, different framing, different lighting`, plus
     the anatomy list from §1;
   - cheap tier for drafts; one output per call until the instruction holds, then 2-3.
4. **Check against the reference, not on its own.** Run
   `python3 ~/.claude/skills/image-edit-fidelity/scripts/ref_diff.py <reference> <output>
   --allow x0,y0,x1,y1` (the box where the change was supposed to happen, in reference
   pixels). It reports how much changed outside that box per grid cell and writes a
   side-by-side and a heat map. Then go through `reference_inventory.md` line by line on the
   output: people count and identity, each object and its position, background, light,
   framing, text. Any `KEEP` item that changed is a defect, even a small one.
5. **Repair instead of regenerating the whole frame.** When the change is right but the rest
   drifted, paste only the changed region back onto the original:
   `ref_diff.py <reference> <output> --allow <box> --paste-back final.png` (feathered edge, the
   rest of the frame comes from the reference pixel for pixel). If the change itself is wrong,
   tighten the `CHANGE` sentence and add the drifted items to `KEEP` by name; change one thing
   per retry.
6. **Report** to the user what changed and confirm what was verified as kept; name any
   accepted deviation.

## 3. Transfer a part from one reference into another

When the user asks to take one element from a source reference (a jacket, a lamp, a face, a
logo, a sky) and put it into a target reference, exactly two things happen: the named element
is copied from the source, and the named place in the target is replaced by it. Nothing else
moves in either direction:
- from the source, take ONLY the named element: not its background, other people or objects,
  colors, lighting, style or framing;
- in the target, change ONLY the named place: people, their count, faces, poses, clothing,
  objects, setting, light, framing and text stay as in the target (§2 KEEP list built from the
  target's inventory);
- do not add anything "to make it fit" (extra props, shadows of objects that do not exist,
  new people). The only allowed adaptation is the element itself taking the target's
  perspective, scale and light so it sits naturally in the replaced place.

How:
1. Inventory the target (§2) and describe the element in the source precisely (what, color,
   material, shape, details that must survive: buttons, print, logo).
2. Crop the source tightly around the element (respect the model's minimum side, 384 px for
   Qwen) before uploading, so the model has nothing else to borrow from it. Put the target in
   the position that sets the output size.
3. Prompt structure:
   "Take only [element with key features] from image 1. In image 2, replace [exact place:
   whose, which side, which object] with it, matching image 2's perspective, scale and light.
   Take nothing else from image 1: not its background, people, colors or lighting. Everything
   else in image 2 stays exactly as it is: [KEEP items from the target inventory, people count,
   faces, poses, objects, setting, framing]. Do not add or remove any people or objects."
   Swap the image numbers if the model wants the base first.
4. Check with `ref_diff.py <target> <output> --allow <box of the replaced place>`: changes
   outside the box are defects; repair with `--paste-back`. Also compare the transferred
   element with the source crop: shape, color, print and details must match.

### Head swap

The head of a person from image 1 onto a person in image 2 is the strictest case of this rule.
On the target person ONLY the head is replaced: face, facial features, skin of the face, hair
and ears come from image 1; head angle, tilt, gaze direction, scale and the scene's light
follow the target so the head sits on the existing neck. Everything else of the target person
stays as in image 2: body, build, neck and shoulders, clothing, pose, hands, accessories below
the head; other people keep their own heads and everything else; the setting, objects and
framing do not change. Nothing from image 1 besides the head (its clothing, body, background,
other people) appears in the output.
- Before the call, settle the ambiguous parts with the user only if they exist: headwear,
  glasses, earrings, beard, and whether the target's hairstyle or the source's is wanted
  (default: everything that belongs to the head comes from image 1).
- Source crop: head and hair only, from the top of the hair to the chin.
- Prompt: "Replace only the head of [target person: position, clothing] in image 2 with the
  head of the person in image 1: same face, facial features, skin tone of the face, hairstyle
  and hair color as in image 1. Keep the head angle, tilt and gaze of the person in image 2
  and match image 2's light. Keep this person's body, neck, shoulders, clothing, pose and hands
  from image 2 unchanged. Keep [other people: count, who] with their own faces, and [setting,
  objects, framing] unchanged. One head, two arms, two legs. Take nothing else from image 1.
  Do not add or remove any people or objects."
- Check: `ref_diff.py <target> <output> --allow <box around the target head and hair>`; the
  face matches image 1 side by side; the neck joins without a visible seam or a second neck;
  exactly one head on that body; the other people unchanged. Repair drift outside the box with
  `--paste-back`.
- Some providers refuse face swaps of real people or block them by policy; report a refusal
  to the user instead of working around it.

## 4. Defect check before showing

- Anatomy of every person, background figures included (§1): one head, two eyes, two arms,
  two hands with five fingers, two legs, every limb attached to its own body at the shoulder or
  hip, no fused bodies. Any violation fails the image.
- People and objects: counts, gaze targets, who stands where.
- Edits: `ref_diff.py` against the reference, then every line of `reference_inventory.md`
  (people count and identity, objects and positions, background, light, framing, text); output
  pixel size and aspect equal to the reference.
- Part transfer: the element matches the source crop; nothing else from the source appears.
- Text: every requested string character by character at full size; unrequested background
  signage comes out as pseudo-text: keep it blurred or out of frame, or name its exact text.
- Look: waxy or over-smoothed skin, oversaturation, style drift.

Regenerate only images with real defects; report the defects you accepted. Show results the
way the user reviews media (global instructions: an HTML page in the built-in browser pane).

## Script

`scripts/ref_diff.py REFERENCE OUTPUT [--allow x0,y0,x1,y1 ...] [--grid 4] [--out-dir DIR]
[--paste-back FINAL.png] [--feather 24]` (Pillow). Resizes the output to the reference size
(reports an aspect mismatch), counts changed pixels outside the allowed boxes overall and per
grid cell, flags cells above 8%, writes `refdiff_side_by_side.jpg` and `refdiff_heatmap.jpg`;
`--paste-back` writes the reference with only the allowed boxes taken from the output,
feathered. Thresholds are heuristics: look at the flagged cells yourself.
