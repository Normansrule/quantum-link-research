"""Release gates for skips (audit C01). Locally a missing optional tool (node, Chromium, an optional simulator) skips
its tests. In CI the same skip would let a required job pass without running what it claims to check, so a job lists
what it requires in QLL_REQUIRE (comma-separated words such as node,chromium,qiskit_aer,perceval) and any skip whose
reason names one of them becomes a failure."""
import os

import pytest

pytest_plugins = ["pytester"]

REQUIRED = [w.strip().lower() for w in os.environ.get("QLL_REQUIRE", "").split(",") if w.strip()]


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if REQUIRED and rep.skipped:
        reason = str(rep.longrepr[-1] if isinstance(rep.longrepr, tuple) else rep.longrepr).lower()
        hit = [w for w in REQUIRED if w in reason]
        if hit:
            rep.outcome = "failed"
            rep.longrepr = f"required by this job (QLL_REQUIRE={','.join(REQUIRED)}) but skipped: {reason}"
