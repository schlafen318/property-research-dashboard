# SEO Generation Validation Correction

## Problem

The first production content-generation run produced two proposals, but both were rejected. The model proposed FAQ and protected ownership content for a country page, returned titles outside the required 30–65 character range, and triggered a false positive because ordinary sentence-start words were treated as unsupported entities.

## Design

Keep deterministic safety enforcement unchanged for protected claims, numbers, source evidence, page types, and title lengths. Improve generation success at the source by extending the developer prompt with explicit page-type rules: non-guide pages must return null FAQ fields; every proposed title must be 30–65 characters; every meta description must be 70–165 characters; and fields using protected-topic language must be null.

Replace single-capitalized-token entity detection with consecutive multiword proper-name detection. A new phrase such as `New York` remains an unsupported entity unless present in source context, while ordinary sentence-start words such as `More` and `Which` no longer trigger rejection.

## Verification

Add regression tests that prove the prompt contains the page-type and length constraints and that ordinary sentence-start words are accepted while unsupported multiword proper names are rejected. Run the complete unit suite, Python compilation, static build verification, tracking verification, and a fixture dry run before publishing. After merge, manually trigger the SEO feedback workflow and inspect its generated-content summary.
