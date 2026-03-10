"""
tests/test_vocab.py

Tests for kc.schema.vocab() and VocabDescriptor.
Both are fully implemented — all tests should pass today.

Traceability: see tests/requirements.md
"""

import pytest
from dataclasses import FrozenInstanceError

from kc.schema import vocab, VocabDescriptor


def test_vocab_single_value():
    """vocab() with a single value produces a 1-tuple."""
    v = vocab("a")
    assert v.values == ("a",)


def test_vocab_many_values():
    """vocab() with multiple values preserves them all."""
    v = vocab("a", "b", "c", "d")
    assert v.values == ("a", "b", "c", "d")


def test_vocab_preserves_order():
    """vocab() preserves insertion order, does not sort."""
    v = vocab("z", "a", "m")
    assert v.values == ("z", "a", "m")


def test_vocab_descriptor_is_frozen():
    """VocabDescriptor is a frozen dataclass — mutation should raise."""
    v = vocab("a", "b")
    with pytest.raises(FrozenInstanceError):
        v.values = ("c",)


def test_vocab_descriptor_repr():
    """repr matches the documented format."""
    v = vocab("a", "b")
    assert repr(v) == "vocab('a', 'b')"


def test_vocab_descriptor_equality():
    """Two vocab() calls with the same values produce equal descriptors."""
    v1 = vocab("a", "b")
    v2 = vocab("a", "b")
    assert v1 == v2


def test_vocab_with_duplicate_values():
    """vocab() does not deduplicate — documents current behavior."""
    v = vocab("a", "a")
    assert v.values == ("a", "a")


def test_vocab_with_empty_string():
    """Empty string is a valid vocab value."""
    v = vocab("")
    assert v.values == ("",)
