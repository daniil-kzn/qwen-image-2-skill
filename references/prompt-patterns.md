# Prompt patterns for Qwen-Image-2.0

Templates distilled from the official Qwen examples (2.0 launch blog, 2512 README, rewriting
system prompts). Replace the bracketed parts; drop lines that do not apply. All are written
for `enable_prompt_expansion: false`.

Contents: 1 portrait, 2 product, 3 poster, 4 slide, 5 infographic, 6 comic, 7 calendar/table,
8 vertical calligraphy, 9 edits, 10 negative prompts.

## 1. Photoreal portrait

```
A casual smartphone photo of a [ethnicity] [gender], about [age] years old, [face shape] face,
[eye shape and color], [skin tone] skin with [texture: visible pores, light freckles], [makeup
or none]. [Hair color, length, cut]. She wears [top, fabric], [bottom], [shoes], [accessories].
She [posture], [head tilt], looking [at the camera / toward the left edge of the frame],
[what the right hand does], [what the left hand does]. Behind her [setting with 2-3 concrete
objects]. [Light source and direction], [color temperature], natural tones, unpretentious
composition, [shot size: medium close-up], shallow depth of field. The image contains no
recognizable text.
```

Gaze and movement directions are anchored to the frame ("toward the right edge of the
picture"), not to the subject's own left or right.

## 2. Product shot

```
Commercial studio photograph of [product] made of [material, finish], [color], [shape and
proportions], placed [position] on [surface]. [Brand text, if any: the word "BRAND" printed in
white sans-serif capitals on the front label]. [Props: 1-3]. [Key light direction and
softness], [rim light], soft realistic shadow under the product, [background color/gradient].
Sharp focus on the label, true-to-life colors. No other text appears in the image.
```

## 3. Poster

```
A [style: hand-drawn healing-style / realistic movie / Swiss minimalist] poster. [Main visual:
subject, action, setting]. At the top, the title "[TITLE]" in large bold [font] [color]
letters. Below it, the subtitle "[SUBTITLE]" in smaller [font] [color]. [Speech bubble /
badge / ribbon] with the text "[TEXT]". At the bottom, "[DATE · PLACE]" in [font, color], and
the small credit line "[CREDITS]". The palette is [2-3 colors]; text sits in empty areas and
does not cover the main subject. No other text appears in the image.
```

Dense credit blocks and small print need a zoomed check; keep legally relevant lines (dates,
prices, disclaimers) short or add them in an editor.

## 4. Slide (image of a slide, not an editable file)

```
A modern presentation slide with a [deep blue gradient] background. Title at the top center:
"[TITLE]" in white bold sans-serif. Below, a glowing horizontal timeline with nodes. First
node: "[DATE] [EVENT]". The timeline then splits into two branches: the upper branch is
labeled "[LABEL A]" with nodes "[DATE] [EVENT]" (above it a small picture: [what the picture
shows, with its own text in quotes]) and "[DATE] [EVENT]"; the lower branch is labeled
"[LABEL B]" with nodes ... Both branches merge into a final node "[DATE] [EVENT]" in a large
font with a strong glow. No other text appears in the image.
```

Picture-in-picture: describe each embedded picture in parentheses right after its node; a
"composite: top shows X, bottom shows the same X without Y" keeps the two halves consistent.

## 5. Infographic, multi-column

```
A professional infographic titled "[TITLE]" on a [background]. The layout has three columns.
Left column, heading "[H1]": four stacked cards. Card 1 titled "[...]" shows "[BIG NUMBER]" in
large green digits and the footnote "[...]". Card 2 ... Middle column, heading "[H2]": a
flowchart of boxes connected by black arrows, top to bottom: "[STEP 1]" -> "[STEP 2]" -> ...
Right column, heading "[H3]": a table with header cells "[COL A]" (dark blue background) and
"[COL B]" (green background); row 1 "[LABEL]": "[A1]" and "[B1]" with a green arrow labeled
"[+21.4%]" ... Clean sans-serif typography, aligned text blocks, consistent icon style.
No other text appears in the image.
```

Use illustrative numbers only when the user supplied them; otherwise ask or mark them as
placeholders.

## 6. Comic grid

```
A [rows]x[cols] comic grid, [rows] rows of [cols] panels, separated by white lines, [art
style]. Row 1, from left to right. Panel 1: [setting]. [CHARACTER ID: a boy with glasses in
oil-stained work overalls] [action]. Speech bubble: "[LINE]". Panel 2: [CHARACTER ID, same
words] [action]. Speech bubble: "[LINE]". ... Row 2, from left to right. Panel 1: ...
Dialogue text is centered inside the speech bubbles.
```

Repeat each recurring character's ID phrase verbatim in every panel. More panels means smaller
faces: 2x3 or 3x3 holds identity better than 4x6; check every panel for identity and text.

## 7. Calendar or table

```
[Style] calendar for [month year], vertical composition. TOP: "[MONTH]" centered in
[font, color]. MIDDLE: [illustration]. BOTTOM: a 7-column grid with [N] rows and thin [color]
lines. Row 1 (weekday header in pale grey): "Mon" "Tue" "Wed" "Thu" "Fri" "Sat" "Sun".
Row 2: Monday cell "1", Tuesday cell "2" ... Row 3: ... Cell [X] has a light purple rectangle
under the text "[HOLIDAY]" and a red circle around "[DAY]". All dates in [font, color].
```

Enumerate every cell; the model aligns text to the described grid.

## 8. Vertical calligraphy or poem on an image

```
Traditional [ink-wash / gongbi] painting, vertical composition. [Scene]. The text is written
from top to bottom and from right to left in [named script: regular script / running script /
Slender Gold] calligraphy: "[LINE 1]\n[LINE 2]\n...". Ink density varies naturally, slight
bleed into rice paper. No seals, no colophon, no modern elements.
```

## 9. Edit instructions

Keep each instruction under 800 characters on fal edit endpoints. With a reference image,
append a KEEP clause built from the reference inventory (SKILL.md §4a), for example:

`Change the sofa upholstery to dark green velvet. Keep exactly three people: the girl sitting on the left armrest in a yellow sweater, the man in the middle with a laptop, the boy on the floor on the right with a dog; same faces, poses and places. Keep the floor lamp on the left, the two framed posters on the wall, the coffee table with a teapot and two mugs, the window light from the right, the framing and the camera angle unchanged. Do not add or remove any people or objects.`

Short forms below use "keep everything else unchanged" only for brevity; in real edits
replace it with the named KEEP items.

- Add: `Add a [object with color, size, pose] at [position], [orientation]; keep everything else unchanged.`
- Remove: `Remove the [object] at [position] and fill the area with the surrounding [surface]; keep everything else unchanged.`
- Replace: `Replace the [object] with [new object: key features]; keep its position, scale and lighting.`
- Text: `Replace "[OLD]" with "[NEW]" on the [carrier]; keep the font, color, size and layout.`
- New text on a photo: `In the upper-left corner, add the text "[TEXT]" written from top to bottom and right to left in [script]; do not change anything else in the photo.`
- Background: `Replace the background with [setting]. Keep the person, face, pose, clothing and hair unchanged; match the original light direction from the [side].`
- Outfit: `Change the [garment] of the woman to [new garment, color, fabric]; keep her face, hairstyle, expression, pose and the background unchanged.`
- Expression: `Make the man smile slightly with closed lips; keep his face, identity, hair and clothing unchanged. Subtle and natural.`
- Pose grid from one portrait: `Generate a 3x3 grid of photos of the same person from image 1 in nine different poses; same face, hairstyle and outfit in every panel.` Inspect each tile at full size.
- Multi-image fusion: `Combine the person from image 1 and the person from image 2 into one natural photo: image 1 person on the left in [clothes], image 2 person on the right in [clothes], standing side by side about 30 cm apart, background from image 2, light from the upper left, 50 mm lens look, no compositing seams.`
- Garment transfer: `The girl from image 1 wears the black dress from image 2 and sits in the pose from image 3; keep her face and hair from image 1.`
- Cross-domain: `Use the city photo in image 1 as the base. Do not change the real buildings, streets, vehicles or people; keep the photo realistic. Add three of the cartoon characters from image 2: one lying on top of the building, one peeking from its right side, one sitting on the square in front. Flat graphic style with clear outlines, like a mural.`
- Colorize: `Restore and colorize the photo.`

## 10. Negative prompts

Text-to-image, English (official list, translated):
`low resolution, low quality, deformed limbs, malformed fingers, oversaturated colors, waxy skin, faces without detail, over-smoothed, AI-generated look, chaotic composition, blurry or distorted text`

Text-to-image, Chinese original (README, Qwen-Image-2512):
`低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有AI感。构图混乱。文字模糊，扭曲。`

Edits with a reference (default of `qwen_payload.py`):
`extra people, missing people, different person, changed background, added objects, removed objects, different framing, different lighting`
Add only the failure you saw (`altered face shape`, `misspelled letters, blurred typography`).
