from datetime import date
import pytest
from nldate import parse

TODAY = date(2025, 11, 15)


def test_today() -> None:
    assert parse("today", TODAY) == TODAY


def test_tomorrow() -> None:
    assert parse("tomorrow", TODAY) == date(2025, 11, 16)


def test_yesterday() -> None:
    assert parse("yesterday", TODAY) == date(2025, 11, 14)


def test_next_tuesday() -> None:
    assert parse("next tuesday", TODAY) == date(2025, 11, 18)


def test_in_three_days() -> None:
    assert parse("in 3 days", TODAY) == date(2025, 11, 18)


def test_before() -> None:
    assert parse("5 days before December 1st, 2025", TODAY) == date(2025, 11, 26)


def test_absolute() -> None:
    assert parse("December 1st, 2025", TODAY) == date(2025, 12, 1)


def test_iso() -> None:
    assert parse("2025-12-01", TODAY) == date(2025, 12, 1)


def test_invalid() -> None:
    with pytest.raises(ValueError):
        parse("random nonsense", TODAY)


def test_number_word() -> None:
    assert parse("in two days", TODAY) == date(2025, 11, 17)
