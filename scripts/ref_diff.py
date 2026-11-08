#!/usr/bin/env python3
"""Compare an edited image with its reference and repair drift outside the edit area.

Usage:
  ref_diff.py REFERENCE OUTPUT [--allow x0,y0,x1,y1 ...] [--grid 4] [--out-dir DIR]
              [--paste-back FINAL.png] [--feather 24]

  --allow       box (reference pixels) where the change was requested; repeatable.
  --paste-back  write FINAL: reference everywhere, output only inside the --allow boxes,
                blended with a feathered edge. Requires --allow.

Writes <out-dir>/refdiff_side_by_side.jpg and refdiff_heatmap.jpg, prints the share of
changed pixels outside the allowed boxes overall and per grid cell. The output is resized to
the reference size first (a size mismatch is reported: it usually means content was cropped
or invented). Thresholds are heuristics: re-rendering adds small global noise, so judge cells
by their ranking and look at the flagged ones with your own eyes.
"""
import argparse, os, sys

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFilter
except ImportError:
    sys.exit("Pillow is required: pip install pillow")

CHANGE_LEVEL = 40      # per-pixel gray difference (0-255) counted as a real change
CELL_FLAG = 0.08       # cell flagged when more than 8% of its pixels changed


def parse_box(s, w, h):
    x0, y0, x1, y1 = [int(float(v)) for v in s.split(",")]
    x0, x1 = sorted((max(0, x0), min(w, x1)))
    y0, y1 = sorted((max(0, y0), min(h, y1)))
    return x0, y0, x1, y1


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("reference")
    p.add_argument("output")
    p.add_argument("--allow", action="append", default=[])
    p.add_argument("--grid", type=int, default=4)
    p.add_argument("--out-dir")
    p.add_argument("--paste-back")
    p.add_argument("--feather", type=int, default=24)
    a = p.parse_args()

    ref = Image.open(a.reference).convert("RGB")
    out = Image.open(a.output).convert("RGB")
    W, H = ref.size
    if out.size != ref.size:
        rr, ro = W / H, out.size[0] / out.size[1]
        note = "aspect differs: content was likely cropped or invented" if abs(rr - ro) / rr > 0.01 else "same aspect, rescaled"
        print(f"SIZE  reference {W}x{H}, output {out.size[0]}x{out.size[1]} ({note})")
        out = out.resize((W, H), Image.LANCZOS)
    boxes = [parse_box(b, W, H) for b in a.allow]

    # Light blur suppresses re-rendering noise and sub-pixel shifts.
    g_ref = ref.convert("L").filter(ImageFilter.GaussianBlur(2))
    g_out = out.convert("L").filter(ImageFilter.GaussianBlur(2))
    diff = ImageChops.difference(g_ref, g_out)
    changed = diff.point(lambda v: 255 if v >= CHANGE_LEVEL else 0)

    allow_mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(allow_mask)
    for b in boxes:
        d.rectangle(b, fill=255)
    outside = ImageChops.multiply(changed, ImageChops.invert(allow_mask))

    def share(img, box=None):
        crop = img.crop(box) if box else img
        hist = crop.histogram()
        total = sum(hist)
        return hist[255] / total if total else 0.0

    def allowed_share(box):
        return share(allow_mask, box)

    print(f"OUTSIDE  {share(outside) * 100:.1f}% of pixels outside the allowed area changed "
          f"(level >= {CHANGE_LEVEL}/255)")
    for b in boxes:
        print(f"INSIDE   box {b}: {share(changed, b) * 100:.1f}% changed")

    n = max(1, a.grid)
    rows = []
    flagged = []
    for r in range(n):
        line = []
        for c in range(n):
            box = (c * W // n, r * H // n, (c + 1) * W // n, (r + 1) * H // n)
            if allowed_share(box) > 0.95:
                line.append("  edit")
                continue
            free = 1 - allowed_share(box)
            v = share(outside, box) / free if free > 0 else 0.0
            line.append(f"{v * 100:5.1f}%")
            if v > CELL_FLAG:
                flagged.append((v, r, c, box))
        rows.append(" ".join(line))
    print(f"GRID {n}x{n} (rows top to bottom, changed share outside allowed boxes):")
    for row in rows:
        print("   ", row)
    if flagged:
        flagged.sort(reverse=True)
        print("FLAG  check these cells against the reference inventory:")
        for v, r, c, box in flagged:
            print(f"      row {r + 1} col {c + 1} box {box}: {v * 100:.1f}%")
    else:
        print("OK    no cell outside the allowed area above the flag level; still verify the inventory")

    od = a.out_dir or os.path.dirname(os.path.abspath(a.output))
    os.makedirs(od, exist_ok=True)
    sbs = Image.new("RGB", (W * 2, H), "white")
    sbs.paste(ref, (0, 0))
    sbs.paste(out, (W, 0))
    dd = ImageDraw.Draw(sbs)
    for b in boxes:
        for off in (0, W):
            dd.rectangle((b[0] + off, b[1], b[2] + off, b[3]), outline=(0, 200, 0), width=max(2, W // 400))
    scale = min(1.0, 3000 / sbs.size[0])
    if scale < 1:
        sbs = sbs.resize((int(sbs.size[0] * scale), int(sbs.size[1] * scale)), Image.LANCZOS)
    sbs.save(os.path.join(od, "refdiff_side_by_side.jpg"), quality=90)

    heat = Image.blend(ref.convert("L").convert("RGB"), Image.new("RGB", (W, H), "black"), 0.5)
    red = Image.new("RGB", (W, H), (255, 0, 0))
    heat.paste(red, (0, 0), outside)
    yellow = Image.new("RGB", (W, H), (255, 220, 0))
    heat.paste(yellow, (0, 0), ImageChops.multiply(changed, allow_mask))
    hd = ImageDraw.Draw(heat)
    for b in boxes:
        hd.rectangle(b, outline=(0, 200, 0), width=max(2, W // 400))
    heat.save(os.path.join(od, "refdiff_heatmap.jpg"), quality=90)
    print(f"FILES {od}/refdiff_side_by_side.jpg, {od}/refdiff_heatmap.jpg "
          "(red = changed outside the allowed area, yellow = changed inside)")

    if a.paste_back:
        if not boxes:
            sys.exit("--paste-back needs at least one --allow box")
        mask = allow_mask.filter(ImageFilter.GaussianBlur(max(1, a.feather)))
        final = Image.composite(out, ref, mask)
        final.save(a.paste_back)
        print(f"PASTE {a.paste_back}: reference outside the boxes, output inside, feather {a.feather}px")


if __name__ == "__main__":
    main()
