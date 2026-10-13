#!/usr/bin/env python3
"""ROM-free Quiz 079 semantic/fixed-width/old-stage provenance self-test."""
from __future__ import annotations
import json
from build_quiz_parent_semantic_restore_079 import ROOT,audit
if __name__=="__main__":
    print(json.dumps(audit(ROOT),ensure_ascii=False,indent=2))
