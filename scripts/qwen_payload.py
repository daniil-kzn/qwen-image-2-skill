#!/usr/bin/env python3
"""Build and validate a fal.ai payload for Qwen-Image-2.0.

Usage:
  qwen_payload.py size <ratio|WxH>
      Print a 2K size (multiples of 16, total pixels <= 2048*2048) for a ratio like 16:9.

  qwen_payload.py build --endpoint fal-ai/qwen-image-2/pro/text-to-image \
      --prompt-file prompt.txt [--ratio 16:9 | --size 2688x1536] \
      [--negative default|edit|none|"custom text"] [--expansion off|on] \
      [--n 1] [--seed 42] [--format png] [--image a.png --image b.png] -o payload.json
      Writes the payload for `fal_run.py submit` and prints warnings. Exit code 1 on errors.

  qwen_payload.py check --prompt-file prompt.txt [--endpoint ...] [--images N]
      Only the prompt checks (length, quotes, image references, scripts).
"""
import argparse, json, math, os, re, sys

MAX_PIXELS = 2048 * 2048
MIN_PIXELS = 512 * 512
# Alibaba-recommended 2K sizes; other ratios are computed.
PRESETS = {
    "1:1": (2048, 2048), "16:9": (2688, 1536), "9:16": (1536, 2688),
    "4:3": (2368, 1728), "3:4": (1728, 2368),
}
NEG_DEFAULT = ("low resolution, low quality, deformed limbs, malformed fingers, oversaturated "
               "colors, waxy skin, faces without detail, over-smoothed, AI-generated look, "
               "chaotic composition, blurry or distorted text")
NEG_EDIT = ("extra people, missing people, different person, changed background, added objects, "
            "removed objects, different framing, different lighting")
EDIT_PROMPT_LIMIT = 800          # fal edit schema
T2I_TOKEN_WARN = 1300            # Model Studio truncates after this many tokens
NEG_LIMIT = 500

errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def parse_ratio(s):
    m = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*[:/x]\s*(\d+(?:\.\d+)?)\s*", s)
    if not m:
        raise ValueError(f"bad ratio {s!r}, expected like 16:9")
    return float(m.group(1)), float(m.group(2))


def size_for_ratio(ratio):
    key = ratio.replace(" ", "")
    if key in PRESETS:
        return PRESETS[key]
    a, b = parse_ratio(ratio)
    target = a / b
    best = None
    for h in range(16, 8192, 16):
        w = int(round(h * target / 16.0)) * 16
        if w < 16 or w * h > MAX_PIXELS:
            continue
        e = abs(w / h - target) / target
        if e > 0.005:
            continue
        if best is None or w * h > best[0] * best[1]:
            best = (w, h)
    if best is None:
        raise ValueError(f"no 2K size within 0.5% of {ratio}")
    return best


def check_size(w, h):
    if w % 16 or h % 16:
        warn(f"size {w}x{h}: sides are not multiples of 16, the service rounds them")
    if w * h > MAX_PIXELS:
        err(f"size {w}x{h}: {w*h} px exceeds 2048x2048")
    if w * h < MIN_PIXELS:
        err(f"size {w}x{h}: below 512x512")
    if w * h < 0.6 * MAX_PIXELS:
        warn(f"size {w}x{h} is {w*h/1e6:.1f} MP; native 2K is 4.2 MP")


def estimate_tokens(text):
    cjk = len(re.findall(r"[぀-ヿ㐀-䶿一-鿿가-힯]", text))
    rest = re.sub(r"[぀-ヿ㐀-䶿一-鿿가-힯]", " ", text)
    words = len(re.findall(r"\S+", rest))
    return cjk + int(math.ceil(words * 1.35))


def quoted_strings(text):
    out = re.findall(r'"([^"\n]{1,400})"', text)
    out += re.findall(r"“([^”]{1,400})”", text)
    out += re.findall(r"「([^」]{1,400})」", text)
    return out


def check_prompt(prompt, endpoint, n_images, expansion):
    is_edit = endpoint is not None and "edit" in endpoint
    chars = len(prompt)
    toks = estimate_tokens(prompt)
    if is_edit and chars > EDIT_PROMPT_LIMIT:
        err(f"prompt is {chars} characters; fal edit endpoints accept {EDIT_PROMPT_LIMIT}")
    if toks > T2I_TOKEN_WARN:
        warn(f"prompt is about {toks} tokens; Model Studio truncates after {T2I_TOKEN_WARN}, "
             "fal states no limit for text-to-image: put exact text and layout first")
    if prompt.count('"') % 2:
        err('odd number of ASCII double quotes: a quoted string is not closed')
    if prompt.count("“") != prompt.count("”"):
        err("unbalanced curly quotes “ ”")
    if prompt.count("「") != prompt.count("」"):
        err("unbalanced corner brackets 「 」")
    strings = quoted_strings(prompt)
    if strings and expansion:
        warn("prompt has quoted text but prompt expansion is on: the rewrite may alter it; "
             "use --expansion off")
    other = [s for s in strings if re.search(r"[Ѐ-ӿͰ-Ͽ֐-ۿ฀-๿]", s)]
    if other:
        warn("quoted text in a script outside Chinese/English (e.g. Cyrillic): "
             f"{other[:3]} - not officially supported, see references/observations.md")
    refs = [int(x) for x in re.findall(r"(?i)\b(?:image|picture|img|figure)\s*(\d)", prompt)]
    refs += [int(x) for x in re.findall(r"图片?\s*(\d)", prompt)]
    if is_edit:
        if refs and max(refs) > n_images:
            err(f"prompt refers to image {max(refs)} but only {n_images} image(s) are attached")
        if n_images > 1 and not refs:
            warn("several input images but the prompt never says which is image 1/2/3")
        if not re.search(r"(?i)\b(keep|unchanged|do not change|don't change|preserve)\b|保持|不要改变|请勿更改", prompt):
            warn("edit prompt has no preservation clause (keep ... unchanged), see SKILL.md 4a")
        elif not re.search(r"(?i)add or remove|添加或删除|增加或减少", prompt):
            warn("edit prompt does not say 'Do not add or remove any people or objects' (SKILL.md 4a)")
        if re.search(r"(?i)\b(everything else|the rest)\b", prompt) and not re.search(r"\d|\b(two|three|four|five|both)\b", prompt, re.I):
            warn("preservation clause is generic ('everything else'): name the people count and key objects from the inventory")
    elif refs:
        warn("text-to-image prompt mentions image N: did you mean an edit endpoint?")
    if re.search(r"(?i)\b(8k|masterpiece|best quality|ultra hd|4k)\b", prompt):
        warn("quality tags (8K, masterpiece, ultra HD) push toward the AI look; describe instead")
    return chars, toks


def prepare_image(path, out_dir):
    path = os.path.abspath(os.path.expanduser(path))
    if not os.path.isfile(path):
        err(f"image not found: {path}")
        return path
    size = os.path.getsize(path)
    if size > 10 * 1024 * 1024:
        err(f"{path}: {size/1e6:.1f} MB, limit 10 MB")
    try:
        from PIL import Image
    except ImportError:
        warn("Pillow not installed: image size and alpha not checked")
        return path
    with Image.open(path) as im:
        w, h = im.size
        if min(w, h) < 384 or max(w, h) > 5000:
            err(f"{path}: {w}x{h}, each side must be 384-5000 px")
        has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
        if has_alpha:
            rgb = Image.new("RGB", im.size, (255, 255, 255))
            rgb.paste(im.convert("RGBA"), mask=im.convert("RGBA").split()[-1])
            base = os.path.splitext(os.path.basename(path))[0]
            new = os.path.join(out_dir, f"{base}_rgb.png")
            rgb.save(new)
            warn(f"{os.path.basename(path)} has alpha (fal rejects it): flattened onto white -> {new}")
            return new
    return path


def ref_size(path):
    """Size of the reference scaled into the 512^2..2048^2 window, sides multiples of 16,
    aspect kept as close as possible."""
    try:
        from PIL import Image
        with Image.open(path) as im:
            w0, h0 = im.size
    except Exception:
        return None, None
    s = min(1.0, math.sqrt(MAX_PIXELS / (w0 * h0)))
    s = max(s, math.sqrt(MIN_PIXELS / (w0 * h0)))
    w = max(16, int(w0 * s) // 16 * 16)
    h = max(16, int(h0 * s) // 16 * 16)
    return w, h


def cmd_size(a):
    s = a.ratio
    m = re.fullmatch(r"(\d+)x(\d+)", s)
    if m:
        w, h = int(m.group(1)), int(m.group(2))
        check_size(w, h)
    else:
        w, h = size_for_ratio(s)
    print(f"{w}x{h}  ({w*h/1e6:.2f} MP, ratio {w/h:.4f})")


def cmd_check(a):
    prompt = open(a.prompt_file, encoding="utf-8").read().strip()
    chars, toks = check_prompt(prompt, a.endpoint, a.images, a.expansion == "on")
    print(f"prompt: {chars} chars, ~{toks} tokens")


def cmd_build(a):
    prompt = open(a.prompt_file, encoding="utf-8").read().strip()
    is_edit = "edit" in a.endpoint
    if not a.endpoint.startswith(("fal-ai/qwen-image-2/", "alibaba/qwen-image")):
        warn(f"endpoint {a.endpoint} is not a Qwen-Image-2.0 endpoint")
    out_dir = os.path.dirname(os.path.abspath(a.output)) or "."
    images = [prepare_image(p, out_dir) for p in (a.image or [])]
    if is_edit and not (1 <= len(images) <= 3):
        err(f"edit needs 1-3 images, got {len(images)}")
    if not is_edit and images:
        err("images given for a text-to-image endpoint")
    chars, toks = check_prompt(prompt, a.endpoint, len(images), a.expansion == "on")

    payload = {"prompt": prompt}
    neg = a.negative
    if neg == "default":
        neg = NEG_EDIT if is_edit else NEG_DEFAULT
    elif neg == "edit":
        neg = NEG_EDIT
    elif neg == "blank":
        neg = " "
    elif neg == "none":
        neg = None
    if neg is not None:
        if len(neg) > NEG_LIMIT:
            err(f"negative prompt is {len(neg)} characters, limit {NEG_LIMIT}")
        payload["negative_prompt"] = neg

    if a.size:
        w, h = map(int, a.size.lower().split("x"))
    elif a.ratio:
        w, h = size_for_ratio(a.ratio)
    else:
        w = h = None
    if w:
        check_size(w, h)
        payload["image_size"] = {"width": w, "height": h}
    elif is_edit and images:
        w, h = ref_size(images[-1])
        if w:
            payload["image_size"] = {"width": w, "height": h}
            print(f"INFO  output size {w}x{h} taken from the base reference {os.path.basename(images[-1])}")
        else:
            warn("could not read the base reference size: output follows the last input image")
    else:
        w, h = PRESETS["1:1"]
        payload["image_size"] = {"width": w, "height": h}
        warn("no size given: using 2048x2048 instead of the fal default 1024x1024")

    payload["enable_prompt_expansion"] = a.expansion == "on"
    lim = 6 if is_edit else 4
    if not 1 <= a.n <= lim:
        err(f"--n {a.n}: this endpoint takes 1-{lim}")
    payload["num_images"] = a.n
    if a.seed is not None:
        payload["seed"] = a.seed
    payload["output_format"] = a.format
    if images:
        payload["image_urls"] = [f"@file:{p}" for p in images]

    for wmsg in warnings:
        print("WARN ", wmsg)
    for emsg in errors:
        print("ERROR", emsg)
    if errors:
        sys.exit(1)
    with open(a.output, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    size_s = f"{w}x{h}" if w else "from last image"
    print(f"OK {a.output}: {chars} chars ~{toks} tokens, size {size_s}, n={a.n}, "
          f"expansion={'on' if payload['enable_prompt_expansion'] else 'off'}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("size")
    s.add_argument("ratio")
    s.set_defaults(fn=cmd_size)
    c = sub.add_parser("check")
    c.add_argument("--prompt-file", required=True)
    c.add_argument("--endpoint", default="fal-ai/qwen-image-2/pro/text-to-image")
    c.add_argument("--images", type=int, default=0)
    c.add_argument("--expansion", choices=["on", "off"], default="off")
    c.set_defaults(fn=cmd_check)
    b = sub.add_parser("build")
    b.add_argument("--endpoint", required=True)
    b.add_argument("--prompt-file", required=True)
    g = b.add_mutually_exclusive_group()
    g.add_argument("--ratio")
    g.add_argument("--size", help="WxH, e.g. 2688x1536")
    b.add_argument("--negative", default="default")
    b.add_argument("--expansion", choices=["on", "off"], default="off")
    b.add_argument("--n", type=int, default=1)
    b.add_argument("--seed", type=int)
    b.add_argument("--format", choices=["png", "jpeg", "webp"], default="png")
    b.add_argument("--image", action="append")
    b.add_argument("-o", "--output", required=True)
    b.set_defaults(fn=cmd_build)
    a = p.parse_args()
    try:
        a.fn(a)
    except ValueError as e:
        print("ERROR", e)
        sys.exit(1)
    if a.cmd != "build":
        for wmsg in warnings:
            print("WARN ", wmsg)
        for emsg in errors:
            print("ERROR", emsg)
        if errors:
            sys.exit(1)


if __name__ == "__main__":
    main()
