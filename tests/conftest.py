"""Shared pytest fixtures and command-line options."""

from __future__ import annotations

import pytest

from src.config import set_reference_date


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--date",
        default=None,
        help="Run tests as if today were this date (DD-MM-YYYY).",
    )


@pytest.fixture(scope="session", autouse=True)
def _apply_reference_date(request: pytest.FixtureRequest) -> None:
    date_arg = request.config.getoption("--date")
    if date_arg:
        set_reference_date(date_arg)
