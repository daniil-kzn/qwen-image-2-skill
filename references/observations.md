# Qwen-Image-2.0: dated observations

Observations, not guarantees. Add each new finding with a date, endpoint and settings; never
delete a failure, mark it superseded instead.

| Date | Endpoint / settings | Observation |
|------|---------------------|-------------|
| 2026-11-08 | fal catalog | all four `fal-ai/qwen-image-2/*` endpoints listed as `deprecated` (since 2026-08-18); schemas and prices still served |
| 2026-11-08 | `fal-ai/qwen-image-2/text-to-image`, 1728x2368, expansion off, seed 20261108, 974-char prompt | deprecated endpoint still served the request, 16 s, 0.035 USD; returned exactly the requested 1728x2368 (no 800-char limit hit on T2I). Realistic chalkboard photo, layout as described (item left, price right column). English and digits exact: "MORNING MENU", "Cappuccino", "250 ₽", "Open 8:00-22:00". Cyrillic: 1 of 3 strings exact ("Сырники со сметаной", wrapped to 2 lines); "Свежая выпечка каждый день" came out "Свежая ниҥечка овемй день", "Круассан с миндалём" as "Круансан с миналём". Small background signage = pseudo-text. Conclusion: Russian text is unreliable, check every word and plan an edit pass or editor overlay |
