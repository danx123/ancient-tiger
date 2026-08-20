"""
zuma_bridge.py
---------------
Single import point used by physics.py / collision.py / chain.py.

Tries the compiled Rust extension `zuma_core` first (fast path). If the
wheel isn't installed (e.g. dev machine without the .pyd, or a fresh clone
before `maturin develop` / `pip install` was run), transparently falls back
to zuma_core_fallback.py - pure Python, same API, same results, just slower.

Nothing else in the codebase needs to know which backend is active.

    from games.zuma_bridge import core, RUST_AVAILABLE
    core.vec_distance(x1, y1, x2, y2)
    core.PathCore(width, height, level)
"""

try:
    import zuma_core as core
    RUST_AVAILABLE = True
except ImportError:
    from . import zuma_core_fallback as core  # relative import inside `games` package
    RUST_AVAILABLE = False

print(f"[zuma_bridge] backend = {'RUST (zuma_core)' if RUST_AVAILABLE else 'PYTHON FALLBACK (zuma_core_fallback)'}")
