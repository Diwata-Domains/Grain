# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT
"""grain.engine.kernel is a re-export shim over grain_core.kernel.

The reducer's own behaviour is tested in the grain-core distribution
(`packages/grain-core/tests/test_kernel.py`). Here we only assert the shim: the address
`grain.engine.kernel` resolves to the same objects grain-core defines, and importing it does not
drag the engine onto the CLI startup graph.
"""

from __future__ import annotations


def test_shim_reexports_the_same_objects():
    import grain.engine.kernel as shim
    import grain_core.kernel as core

    for name in core.__all__:
        assert getattr(shim, name) is getattr(core, name), f"{name} is not re-exported identically"
    assert set(shim.__all__) == set(core.__all__)


def test_concurrent_modification_identity_crosses_the_shim():
    # `except grain.engine.kernel.ConcurrentModification` must catch what grain_core raises.
    from grain.engine.kernel import ConcurrentModification as ShimError
    from grain_core.kernel import ConcurrentModification as CoreError

    assert ShimError is CoreError


def test_cli_does_not_import_the_engine():
    """The kernel is off the startup graph — `grain status` cannot be broken by it."""
    import subprocess
    import sys

    code = (
        "import sys; import grain.cli; "
        "sys.exit(1 if any(m.startswith('grain.engine') for m in sys.modules) else 0)"
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=60)
    assert proc.returncode == 0, proc.stderr.decode()
