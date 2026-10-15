# Checkpoint103 — screenshot defects and a wider Japanese-text audit

2026-10-15. User flagged both team labels, ambiguous “Kim Ngưu” and the weak
uppercase L, then requested another error/Japanese review. Images089/095 were
old, so all acceptance pictures were recaptured against the final103 candidate.

Changes:

- Both team-selection labels now use the existing private white/black palette7
  and consistent alignment. The original colored strip backgrounds are flood
  cleared only through transparent/background indices0/1/2. Mascot foreground
  is preserved; text masks are taken from the existing102 word bitmap.
  Modified tiles are cloned; the two102 private assets expand only into guarded
  FF gaps. No shared native asset, header or palette is changed.
- Uppercase L had a one-pixel stem. Its stem/foot are strengthened. Twelve
  lowercase Vietnamese horn forms also gain two pixels each. “Kim Ngưu” was
  already encoded correctly, but the horn inư was a weak single-pixel mark.
  All160 mapped glyphs were compared: zero unintended collisions, unchanged
  unrelated glyphs and unchanged neighboring font-cell bits.
- The live explanation-page pointer table exposed an actual missed Japanese
  line: mother introduction at32874, table31377, slot20/page1. Only the age
  digits had previously been converted. New “Mẹ Sumire 40 tuổi” uses exactly
  the same34-byte physical frame, with a safe first-line column4. Other rows,
  line markers and pointers remain unchanged. A native correct answer was used
  to reach the explanation and visually confirm the complete Vietnamese line.

`audit_active_text_103.py` follows the actual bank06 tables:50 main questions,
150 choices,150 explanation-page references, plus all157 canonical Fortune
fields through the four relocated pointers. It rejects102 on the missed
mother line and passes103. Remaining native glyphs in this audited subset are
the intentional 一雄/和雄 name-spelling alternatives in slot39, which would be
indistinguishable if replaced by identical Latin spellings. This is an encoding
audit, not a semantic certification or full-game coverage percentage.

Final Snes9x/libretro sweep exercises50 injected question slots/150 answer
selections on the exact final IPS. Wrong choices naturally keep the question
on screen until a correct choice; do not describe this as150 independently
displayed explanation pages. Mother explanation was reached separately by
selecting the native correct position. All five Fortune ranks and the Lam
color case were rendered using controlled WRAM values. VS setup/selection,
native match completion and result screen were exercised again.

Wider review found more unfinished graphics: minigame names on balloons and
intro artwork, Japanese character nameplates, Paint title/Start prompt/finish
button, and Karaoke title/start choices. All28 canonical Karaoke lyric source
rows still contain Japanese; their translations are source drafts, not inserted
runtime text. Paint and Karaoke were entered separately through menu entries4
and6. Sound is entry7. Do not confuse the Paint screen with Karaoke.

An additional source check covered267 distinct Story manifest records. All
ordinary text is V2; seven previously protected leading xxF3 pairs remain in
special046 records. Their structural/visibility status needs dedicated runtime
tracing, so they are not automatically classified as visible Japanese words.
Whole Story progression, victory/final-victory/ending and full lyric timing are
still unverified. Original Japanese copyright-owner credits remain intentional.

Rebuild one cumulative IPS with `tools/build_cumulative_103.py`, original ROM,
historical043 ZIP and local Tahoma Bold/Tahoma paths. No ROM/font binary is
committed. Final IPS127,963 bytes, SHA256:
`5a5a46ec63eea4c5aa9f876b008b112e31f4cef4ab4bd470b33e67cc9ccfc9c7`.
Patched ROM SHA256:
`10975990b087348e48c080d7891721eccef0fdb2d5ed6c108e404cb37bef5eef`.

Whole-game completion remains FALSE. Next work is the confirmed residual
graphics/Paint/Karaoke insertion, then complete gameplay and editorial QA.
Historic Quiz scanner counts remain279/381: this repairs an existing partially
translated record, not a new scanner discovery.
