#!/usr/bin/env python3
from __future__ import annotations

from trace_g2_start_flow import (
    RESOURCE_INTERPRETER,
    WORKER_INIT,
    control_flow,
    exact_long_calls,
    file_to_cpu,
    resource_calls,
)


def main() -> int:
    data = bytearray(0x200000)

    off = 0x44000
    data[off:off + 7] = bytes.fromhex("A2 23 AF 22 55 E2 80")
    rows = resource_calls(data, off - 8, off + 16)
    assert len(rows) == 1
    assert rows[0]["script_cpu"] == 0x82AF23

    woff = off + 0x20
    data[woff:woff + 4] = bytes((
        0x22,
        WORKER_INIT & 0xFF,
        (WORKER_INIT >> 8) & 0xFF,
        (WORKER_INIT >> 16) & 0xFF,
    ))
    workers = exact_long_calls(data, WORKER_INIT, off, off + 0x40)
    assert len(workers) == 1
    assert workers[0]["source_file"] == woff

    jsl_off = off + 0x40
    data[jsl_off:jsl_off + 4] = bytes.fromhex("22 55 E2 80")
    jsr_off = off + 0x50
    data[jsr_off:jsr_off + 3] = bytes.fromhex("20 4E CB")
    flows = control_flow(data, off + 0x38, off + 0x58)
    assert any(r["op"] == "JSL" and r["target_cpu"] == RESOURCE_INTERPRETER for r in flows)
    assert any(r["op"] == "JSR" and (r["target_cpu"] & 0xFFFF) == 0xCB4E for r in flows)

    assert file_to_cpu(0x44B4E) == 0x88CB4E

    print("g2_targeted_trace_selftest=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
