# Chibi Maruko-chan SNES — Checkpoint 071: recovery from any historical 039–043 archive

Date: 2026-10-12. Branch: `chibi-maruko-bootstrap-01`.

## Objective: stop requiring one specific old ZIP

Earlier checkpoint 070 could rebuild the integrated 061 cumulative patch only if the **exact** historical checkpoint 043 IPS/ZIP was accessible. It was not: the original `Chibi_043_G0G1_176Fields_Story58_Content_First_UNTESTED.zip` is present in Library *metadata*, but the raw-byte materialization response remains `This Project file does not have an authorized raw-byte materialization path`. The user-provided original Japanese 2MiB SFC **is** accessible, with SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.

This checkpoint adds **`tools/recover_from_any_039_to_043_archive_071.py`**, a concrete fallback. With a user-owned historical **ZIP or IPS from any checkpoint 039, 040, 041, 042 or 043**, it:

1. Reads ZIP entries **in memory only**, without extracting paths or game files. Refuses excessively large ZIPs, unrelated formats or unsigned/source-unknown IPS blobs.
2. Identifies checkpoint provenance **only by the precise original IPS size and SHA256**, never by ZIP filename. If multiple approved patches are in a ZIP, selects the highest checkpoint.
3. Validates the exact Japanese original ROM hash, replays the trusted source patch, then invokes each missing **existing original guarded build function** through checkpoint 043. It verifies the exact historical clean-ROM IPS SHA, per-stage ROM length and IPS replay at each step. **No intermediary commercial ROM file is written.**
4. Invokes the already authored `rebuild_content_first_061_full_chain.py` to rebuild 044 through 061, validates complete clean-ROM IPS replay and result SHA, and writes **only** cumulative IPS plus JSON QA.
5. Keeps `release_approved: false`, `emulator_tested: false` until actual SNES gameplay acceptance.

Exact original source-patch identities pinned in the script:

| Accepted checkpoint | Original clean-ROM IPS size | Exact SHA256 |
|---|---:|---|
| 039 | 21,130 bytes | `97c0e41b354b0dda3ea7c0c292b5aef236586e279870962fd0d4f3398285008c` |
| 040 | 21,727 bytes | `2bfdcc64973bc31ce268fa7e68a6118808c633b10d1437b7f811ac290616e580` |
| 041 | 22,100 bytes | `2117bc6e165f2c86263e74a637b6961a13f79257fccd9f02152a769fe1deb962` |
| 042 | 23,105 bytes | `3e3c3de245a9a0a6648b2e62eff44a72093ef1e2e9cfcb1cf013ff6c4cbb5035` |
| 043 | 28,135 bytes | `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50` |

These are the exact anchors from existing committed, reviewed build code. The tool performs no heuristic reconstruction based on incorrect hashes. Any byte mismatch fails closed.

### Usage

From the cloned project's game directory, with the user's original clean Japanese SFC and **one** original old ZIP or IPS:

```bash
python tools/recover_from_any_039_to_043_archive_071.py clean.sfc Chibi_041_G0G1_92UIFortuneQuiz_Content_First_UNTESTED.zip --ips chibi_combined061.ips --report chibi061_qa.json --allow-untested
```

The example ZIP is an *option*, not a recovered file. Substituting the user's original 039, 040, 042, 043 or exact extracted IPS also works when its SHA matches. A bogus ZIP, a renamed different IPS and unreviewed patches are refused. The entire build may still fail if the user's historical source content differs from source code; this must be audited, not bypassed.

## CI negative tests

Added `tools/selftest_recovery_071.py`, a **ROM-free** safety test:

- Pins every 039–043 SHA to the exported constants of the original `build_content_first_040_fortune.py`, `041_quiz.py`, `042_story_safe_segments.py`, `043_story_58.py` modules.
- Checks that original build functions are importable.
- Constructs a fake same-length `.ips` and ZIP containing fake `.ips`, ensures they are rejected.
- Ensures a missing archive is rejected rather than silently claiming a restoration.

The new test is connected to `.github/workflows/chibi-snes-source-qa.yml`. **Actual Github Actions result must be checked before reporting PASS.** The previous source and graphics workflow jobs were green after fixing 042/043/055 syntax faults in checkpoint070.

**Important QA distinction:** a passing ROM-free negative test proves that stage SHA contracts and rejection logic work; it does **not** prove a successful historical 039–043 reconstruction or an integrated 061 game build. No historical raw ZIP has been retrieved yet. No emulator has been run.

## Accurate project status

- **279/381** unique Quiz source records prepared; 102 not staged. The 81 exact full Quiz choices from checkpoint069 are still a **byte-level hybrid CP932/V2 research experiment**, not playable/renderer-accepted.
- To unlock real integration, a user-uploaded 039–043 ZIP/IPS is still required. The new script significantly increases acceptable checkpoint choices, but cannot manufacture absent historical font or graphics bytes.
- Following an actual verified 061 combined IPS build, test original-Japanese relocated choice, Vietnamese font rendering, Quiz choice navigation and correctness, plus Fortune's four too-long items and G3 result sprites.

Priority remains **content integrity first, font polish last**, and no pointless downloadable micro-patches.
