#!/usr/bin/env python3
from __future__ import annotations

from build_g2_conversation_direct_probe_003 import (
    FIELD_BYTES,
    FIELDS,
    LINE_BREAK,
    build_payload,
)


def main() -> int:
    chars = set("".join("".join(lines) for _off, lines in FIELDS))
    enc = {ch: bytes((0x84, 0x40 + i)) for i, ch in enumerate(sorted(chars))}
    for _off, lines in FIELDS:
        payload = build_payload(lines, enc)
        assert len(payload) == FIELD_BYTES
        assert payload[32:34] == LINE_BREAK
        assert payload[68:70] == LINE_BREAK
        assert payload[104:106] == LINE_BREAK
        for start, end in ((2, 32), (34, 68), (70, 104)):
            # Quotes are outside this check; all runtime text/padding bytes are paired 0x84xx.
            chunk = payload[start:end]
            for i in range(0, len(chunk), 2):
                if chunk[i:i+2] in (bytes.fromhex("8176"),):
                    continue
                assert chunk[i] == 0x84
    print("g2_direct_text_probe_003_selftest=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
