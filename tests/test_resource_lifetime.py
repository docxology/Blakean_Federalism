# Copyright (c) 2026 Daniel Ari Friedman
"""Real SQLite fixture lifetime checks on the current Python runtime."""

import gc


def test_captured_projection_closes_its_database(recwarn, captured):
    # Given the real corpus fixture, force collection while warnings are observed.
    assert captured[1].joinpath("passages.sqlite").is_file()
    gc.collect()
    assert not [
        str(warning.message) for warning in recwarn if issubclass(warning.category, ResourceWarning)
    ]
