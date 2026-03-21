"""
tests/test_exceptions.py

Tests for kc.exceptions — ValidationError, UnknownQueryError, SchemaError.
All exception classes are fully implemented — all tests should pass today.

Traceability: see tests/requirements.md
"""

from knowledgecomplex import ValidationError, UnknownQueryError, SchemaError


def test_validation_error_is_exception():
    """ValidationError is a subclass of Exception."""
    assert issubclass(ValidationError, Exception)


def test_validation_error_has_report_attribute():
    """ValidationError carries a .report string."""
    e = ValidationError("test message", "report text")
    assert e.report == "report text"


def test_validation_error_report_type():
    """The .report attribute is always a string."""
    e = ValidationError("msg", "report")
    assert isinstance(e.report, str)


def test_validation_error_str_includes_report():
    """str(ValidationError) includes both message and report."""
    e = ValidationError("something went wrong", "detailed SHACL report")
    s = str(e)
    assert "something went wrong" in s
    assert "detailed SHACL report" in s


def test_unknown_query_error_is_exception():
    """UnknownQueryError is a subclass of Exception."""
    assert issubclass(UnknownQueryError, Exception)


def test_unknown_query_error_message():
    """UnknownQueryError preserves its message."""
    e = UnknownQueryError("no such template 'foo'")
    assert str(e) == "no such template 'foo'"


def test_schema_error_is_exception():
    """SchemaError is a subclass of Exception."""
    assert issubclass(SchemaError, Exception)
