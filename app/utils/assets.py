"""Utilities for serving versioned static assets."""

from __future__ import annotations

import hashlib
import os

from flask import current_app, url_for

_asset_cache: dict[str, tuple[int, str | None]] = {}


def asset_url(filename: str) -> str:
    """Return a cache-busted URL for a static asset.

    Appends a short content hash as a ``v`` query parameter when the asset exists,
    ensuring browsers fetch the latest version after rebuilds while still allowing
    CDN/browser caching between changes.
    """

    app = current_app._get_current_object()  # type: ignore[attr-defined]
    static_folder = app.static_folder or ""
    path = os.path.join(static_folder, filename)

    version: str | None = None
    try:
        stat_result = os.stat(path)
    except (FileNotFoundError, NotADirectoryError):
        stat_result = None  # type: ignore[assignment]

    if stat_result is not None:
        mtime_marker = int(stat_result.st_mtime_ns)
        cached = _asset_cache.get(filename)
        if not cached or cached[0] != mtime_marker:
            digest = _hash_file(path)
            _asset_cache[filename] = (mtime_marker, digest)
            version = digest
        else:
            version = cached[1]

    if version:
        return url_for("static", filename=filename, v=version)
    return url_for("static", filename=filename)


def _hash_file(path: str) -> str | None:
    """Return a short SHA-256 hash prefix for the given file."""

    try:
        with open(path, "rb") as handle:
            digest = hashlib.sha256(handle.read()).hexdigest()
    except OSError:
        return None
    return digest[:12]
