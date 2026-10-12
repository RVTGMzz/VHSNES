#!/usr/bin/env python3
"""ROM-free QA: 061 report shapes from raw builder, 070 and 071 all interoperate.

The actual retail ROM and historical IPS are NOT present in GitHub Actions.
This unit test validates the 076 one-archive integration contract and its
fail-closed behavior, not an emulator run or actual merged ROM build.
"""
from __future__ import annotations
import json
from build_quiz_relocated_81_jobwait_075 import validate_061_baseline_report
from recover_merge_061_81_one_ips_076 import rebuild_one_patch

CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
ROM_SHA="b"*64
IPS_SHA="c"*64
BASE={
    "status":"FULL_043_TO_061_STATIC_ONLY_EMULATOR_UNTESTED",
    "result_061_ROM_sha256":ROM_SHA,
    "release_ready":False,
    "emulator_tested":False,
}
ZIP071={
    "status":"REBUILT_EXACT_043_AND_061_STATIC_ONLY_EMULATOR_UNTESTED",
    "original_clean_ROM_sha256":CLEAN_SHA,
    "final_061_ROM_sha256":ROM_SHA,
    "final_061_clean_ROM_IPS_sha256":IPS_SHA,
    "historical_baseline_stage":"041",
    "original_sfc_emulator_tested":False,
    "release_approved":False,
    "full_061_source_report":dict(BASE),
}
ZIP070={
    **BASE,"checkpoint_043_IPS_sha256":"d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50",
    "final_clean_ROM_IPS_sha256":IPS_SHA,
}

def reject(qa,reason):
    try:
        validate_061_baseline_report(qa,ROM_SHA,IPS_SHA,CLEAN_SHA)
    except AssertionError:
        return
    raise AssertionError("Unexpected accepted tampered 061/071 QA: "+reason)

def main():
    if not callable(rebuild_one_patch):
        raise AssertionError("One-archive integrator missing")
    for name,report in (
        ("direct_061",BASE),("original_043_zip_070",ZIP070),
        ("any_039_to_043_zip_071",ZIP071),
    ):
        result=validate_061_baseline_report(report,ROM_SHA,IPS_SHA,CLEAN_SHA)
        if not result["provenance_hash_fields_agree"]:
            raise AssertionError("Actual stage accepted without a SHA contract: "+name)
    reject({**ZIP071,"final_061_ROM_sha256":"0"*64},"wrong top ROM hash")
    reject({**ZIP071,"full_061_source_report":{**BASE,"result_061_ROM_sha256":"0"*64}},
           "wrong nested ROM hash")
    reject({**ZIP071,"final_061_clean_ROM_IPS_sha256":"0"*64},"wrong patch hash")
    reject({**ZIP071,"original_clean_ROM_sha256":"0"*64},"wrong retail ROM")
    reject({**ZIP071,"historical_baseline_stage":"038"},"untrusted checkpoint")
    reject({**ZIP071,"status":"nonexistent"},"unknown report status")
    reject({**ZIP071,"release_approved":True},"false release acceptance")
    reject({**BASE,"result_061_ROM_sha256":None},"no ROM SHA")
    print(json.dumps({
        "status":"PASS_ROM_FREE_061_TO_075_TO_076_INTEGRATION_QA",
        "positive_report_formats":3,
        "negative_tamper_cases":8,
        "requires_original_039_to_043_archive_for_real_build":True,
        "emulator_tested":False,
        "ROM_or_IPS_created":False,
    },indent=2))

if __name__=="__main__":
    main()
