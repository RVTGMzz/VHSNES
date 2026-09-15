# Translation source layer

This directory holds meaning-first translation data.

Rules:

- `vi_full` is natural Vietnamese source-of-truth and may contain full diacritics.
- Do not shorten `vi_full` to fit ROM fields.
- Runtime-constrained spellings belong in `translation/runtime/`.
- Every row must retain exact Japanese source identity and exact file offset once committed for patching.
- Candidate scanner output is not automatically accepted as source text.
