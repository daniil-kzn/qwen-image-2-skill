# Qwen-Image-2.0 API reference (checked 2026-11-08)

Re-read the live schema before each task: `fal_run.py schema <endpoint>`. Prices and limits
below are observations, not tariffs.

## fal.ai

Status: all four endpoints `deprecated` since 2026-08-18 in the fal catalog; schemas still
served on 2026-11-08. Successor on fal: `alibaba/qwen-image-3/text-to-image` and
`alibaba/qwen-image-3/edit` (active, prompt up to 5000 characters, priced per unit; a
different model that needs its own test before use).

| Endpoint | Required | Price |
|----------|----------|-------|
| `fal-ai/qwen-image-2/text-to-image` | `prompt` | 0.035 USD/image |
| `fal-ai/qwen-image-2/pro/text-to-image` | `prompt` | 0.075 USD/image |
| `fal-ai/qwen-image-2/edit` | `prompt`, `image_urls` | 0.035 USD/image |
| `fal-ai/qwen-image-2/pro/edit` | `prompt`, `image_urls` | 0.075 USD/image |

Common input fields:

| Field | Type, default | Notes |
|-------|---------------|-------|
| `prompt` | string | Chinese and English. Edit: max 800 characters. T2I: no limit stated |
| `negative_prompt` | string, `""` | max 500 characters |
| `image_size` | preset or `{"width","height"}`; T2I default `square_hd` | presets: `square_hd` (1024x1024), `square` (512x512), `portrait_4_3`, `portrait_16_9`, `landscape_4_3`, `landscape_16_9` (all about 1 MP). Total pixels 512x512..2048x2048. Edit default: size of the last input image |
| `enable_prompt_expansion` | bool, `true` | LLM rewrite of the prompt |
| `seed` | int | 0..2147483647 |
| `num_images` | int, 1 | T2I 1-4, edit 1-6 |
| `output_format` | `png` | `jpeg`, `png`, `webp` |
| `enable_safety_checker` | bool, `true` | disabling needs account authorization |
| `sync_mode` | bool, `false` | `true` returns a data URI and skips request history: keep `false` |
| `image_urls` (edit) | list, 1-3 | order = "image 1/2/3"; 384-5000 px per side; max 10 MB; JPEG, PNG without alpha, WEBP |

Output: `{"images": [{"url": ...}], "seed": N}`.

Minimal payloads:

```json
{"prompt": "...", "negative_prompt": "...", "image_size": {"width": 2688, "height": 1536},
 "enable_prompt_expansion": false, "num_images": 1, "output_format": "png"}
```

```json
{"prompt": "Replace \"SALE\" with \"NEW\" on the red banner; keep everything else unchanged.",
 "image_urls": ["@file:/abs/path/poster.png"], "negative_prompt": " ",
 "enable_prompt_expansion": false}
```

## Alibaba Model Studio (DashScope)

Models: `qwen-image-2.0-pro` (= snapshot 2026-04-22; newer snapshot `qwen-image-2.0-pro-2026-06-22`,
older `-2026-03-03`) and `qwen-image-2.0` (accelerated, = `qwen-image-2.0-2026-03-03`).
Generation and editing share one synchronous endpoint:

- Singapore: `POST https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation`
- Beijing: `POST https://{WorkspaceId}.cn-beijing.maas.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation`
- Header `Authorization: Bearer $DASHSCOPE_API_KEY`; keys and hosts are per region and not
  interchangeable. Not configured on this machine as of 2026-11-08.

Body: `{"model": "...", "input": {"messages": [{"role": "user", "content": [ {"image": "..."}x0-3, {"text": "..."} ]}]}, "parameters": {...}}`.
Exactly one message and exactly one `text` item. Images: public URL or
`data:image/png;base64,...`; JPG, PNG, BMP, TIFF, WEBP, GIF (first frame); 384-3072 px
recommended; max 10 MB.

| Parameter | Notes |
|-----------|-------|
| `text` | up to 1300 tokens for the 2.0 series, excess is truncated silently |
| `negative_prompt` | max 500 characters |
| `size` | `"W*H"`, total pixels 512x512..2048x2048. T2I default 2048*2048; edit default about 1024*1024 with the aspect of the last input image. Rounded to multiples of 16 |
| `n` | 1-6 |
| `prompt_extend` | default `true` |
| `watermark` | default `false` ("Qwen-Image" bottom right) |
| `seed` | 0..2147483647 |

Recommended sizes. T2I: 2688*1536 (16:9), 1536*2688 (9:16), 2048*2048, 2368*1728 (4:3),
1728*2368 (3:4). Edit: 1024*1024 or 1536*1536, 1024*1536 / 1536*1024, 1080*1440 / 1440*1080,
1080*1920 / 1920*1080, 2048*872 (21:9).

Response: `output.choices[0].message.content[i].image` (PNG URL, expires after 24 hours:
download at once), `usage.width/height/image_count`. Billing per successful image; failed
calls are free.

## WaveSpeed

`POST https://api.wavespeed.ai/api/v3/wavespeed-ai/qwen-image-2.0/text-to-image`
(`prompt`, `size` "W*H" default 1024*1024, `seed`) and `.../qwen-image-2.0/edit` (`prompt`,
`images` 1-3 URLs, `size`). Prompt max 800 characters. Async: poll
`GET /api/v3/predictions/{id}/result` until `data.status == "completed"`, image in
`data.outputs[0]`. Listed at 0.03 USD per output in November 2026. No key on this machine.

## Open weights

The QwenLM README links no Qwen-Image-2.0 weights (checked 2026-11-08). The open-weight line is
`Qwen/Qwen-Image-2512` (T2I) and `Qwen/Qwen-Image-Edit-2511` (edit), available on fal as
`fal-ai/qwen-image-2512` and `fal-ai/qwen-image-edit-2511` (with LoRA variants). Those are
different models: the prompt rules of this skill mostly carry over, the parameters do not
(they take `num_inference_steps`, `guidance_scale`, and the official 2512 pipeline uses
`true_cfg_scale` 4.0 with 50 steps).

## Sources

- QwenLM/Qwen-Image README and `src/examples/tools/prompt_utils.py`, `prompt_utils_2512.py`
- Qwen blog "Qwen-Image-2.0: Professional infographics, exquisite photorealism", 2026-02-10
- Alibaba Cloud Model Studio: `qwen-image-api`, `qwen-image-edit-api`
- fal: `https://fal.ai/models/<endpoint>/llms.txt`, `fal_run.py schema/price`
- WaveSpeed blog "How to Use Qwen Image 2.0" (November 2026)
