#!/usr/bin/env python3
from __future__ import annotations

from trace_g2_school_front_resources import walk_code_candidates
from trace_g2_start_flow import file_to_cpu


def main() -> int:
    data = bytearray(0x200000)

    # Root $88:9000 -> JSR $9100.
    root_file = 0x41000
    child_file = 0x41100
    assert file_to_cpu(root_file) == 0x889000
    assert file_to_cpu(child_file) == 0x889100

    data[root_file:root_file + 3] = bytes.fromhex("20 00 91")

    # Child contains exact resource call shape:
    # LDX #$AF23 ; JSL $80:E255
    data[child_file:child_file + 7] = bytes.fromhex(
        "A2 23 AF 22 55 E2 80"
    )

    walked = walk_code_candidates(
        data,
        roots=[0x889000],
        radius=0x20,
        max_depth=2,
        code_banks={0x88},
    )

    cpus = {row["cpu"] for row in walked["routines"]}
    assert 0x889000 in cpus
    assert 0x889100 in cpus

    calls = walked["resource_calls"]
    assert len(calls) == 1
    assert calls[0]["routine_cpu"] == 0x889100
    assert calls[0]["script_cpu"] == 0x82AF23

    # Depth gate should stop before the child when set to zero.
    shallow = walk_code_candidates(
        data,
        roots=[0x889000],
        radius=0x20,
        max_depth=0,
        code_banks={0x88},
    )
    assert {row["cpu"] for row in shallow["routines"]} == {0x889000}
    assert shallow["resource_calls"] == []

    print("g2_school_front_resource_collector_selftest=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
