# Runtime candidate layer

Runtime text is renderer/byte-budget specific and must be derived from `translation/source/`.

Current state:

- full Vietnamese glyph support: UNPROVEN
- ASCII renderer support: UNPROVEN
- pointer relocation: UNPROVEN
- field terminators/control semantics: UNPROVEN

Do not mass-generate no-diacritic Vietnamese until the ASCII renderer probe has runtime evidence. If a compact/no-diacritic candidate is needed for diagnostics, retain `vi_full` untouched.
