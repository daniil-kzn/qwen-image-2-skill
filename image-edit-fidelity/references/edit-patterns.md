# Edit instruction patterns (any model)

Image numbers follow the order of attached inputs. Examples assume image 2 is the base; when
the model sets the output from the first image, swap the numbers. Where the model has no
negative prompt field, the closing "Do not add or remove any people or objects" stays in the
prompt as the only exclusion sentence.

## KEEP clause built from the reference inventory (SKILL.md §2)

`Change the sofa upholstery to dark green velvet. Keep exactly three people: the girl sitting on the left armrest in a yellow sweater, the man in the middle with a laptop, the boy on the floor on the right with a dog; same faces, poses and places. Keep the floor lamp on the left, the two framed posters on the wall, the coffee table with a teapot and two mugs, the window light from the right, the framing and the camera angle unchanged. Same natural anatomy for every person: one head, two arms, two legs. Do not add or remove any people or objects.`

Short forms below use "keep everything else unchanged" only for brevity; in real edits replace
it with the named KEEP items.

- Add: `Add a [object with color, size, pose] at [position], [orientation]; keep everything else unchanged.`
- Remove: `Remove the [object] at [position] and fill the area with the surrounding [surface]; keep everything else unchanged.`
- Replace: `Replace the [object] with [new object: key features]; keep its position, scale and lighting.`
- Background: `Replace the background with [setting]. Keep the person, face, pose, clothing and hair unchanged; match the original light direction from the [side].`
- Outfit: `Change the [garment] of the woman to [new garment, color, fabric]; keep her face, hairstyle, expression, pose and the background unchanged.`
- Expression: `Make the man smile slightly with closed lips; keep his face, identity, hair and clothing unchanged. Subtle and natural.`

## Part transfer (SKILL.md §3; image 1 = tight crop of the source part, image 2 = target)

`Take only the brown leather jacket with brass zipper and two chest pockets from image 1. In image 2, replace the grey hoodie of the man on the left with it, matching image 2's perspective, scale and light. Take nothing else from image 1: not its background, people, colors or lighting. Everything else in image 2 stays exactly as it is: two people, same faces, poses and positions, the woman's blue dress, the bench, the trees, the framing. Same natural anatomy for both. Do not add or remove any people or objects.`

## Head swap (SKILL.md §3; image 1 = crop of the source head and hair, image 2 = target)

`Replace only the head of the woman on the right in the green coat in image 2 with the head of the person in image 1: same face, facial features, skin tone of the face, hairstyle and hair color as in image 1. Keep the head angle, tilt and gaze of the woman in image 2 and match image 2's light. Keep her body, neck, shoulders, green coat, pose and hands unchanged. Keep the man on the left with his own face, the café table with two cups and the framing unchanged. One head, two arms, two legs. Take nothing else from image 1. Do not add or remove any people or objects.`

## Object transfer

`Take only the green ceramic table lamp from image 1. In image 2, replace the white lamp on the bedside table on the right with it, same size and position, lit by image 2's window light. Take nothing else from image 1. Keep the bed, the pillows, the painting above the bed, the rug, the window on the left and the framing of image 2 unchanged. Do not add or remove any objects.`

## Garment and pose from several images

`The girl from image 1 wears the black dress from image 2 and sits in the pose from image 3; keep her face and hair from image 1; take nothing else from images 2 and 3.`

## Hand fix (on a crop around the hand, then paste back with ref_diff.py)

`Correct the left hand of the woman: one hand with five fingers in a natural relaxed pose, holding the white cup by its handle; keep the cup, sleeve, skin tone and lighting unchanged.`

## Several people in text-to-image (SKILL.md §1)

```
Exactly [N] people, each with one head, two arms and two legs, anatomically correct with
natural proportions. On the left, [person 1: identity, clothing]; her right hand [action], her
left arm [position]; standing with weight on the right leg. In the center, [person 2] ...; his
left hand rests on the shoulder of the woman on the left, his right hand [action]. On the
right, [person 3] ... They stand about [distance] apart, bodies not overlapping except where
described.
```

Keep hands visible or clearly hidden (pockets, behind the back, out of frame), avoid
interlaced arms and people standing directly behind one another. Gaze and movement directions
are anchored to the frame ("toward the right edge of the picture").

## Exclusion lists

Anatomy: `extra limbs, extra arms, extra legs, extra hands, extra fingers, missing fingers, two heads, extra head, extra eyes, fused bodies, limbs from torso, deformed hands, malformed anatomy`

Edits with a reference: `extra people, missing people, different person, changed background, added objects, removed objects, different framing, different lighting`

Add only the failure you saw (`altered face shape`, `misspelled letters`).
