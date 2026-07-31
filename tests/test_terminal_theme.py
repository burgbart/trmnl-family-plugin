"""Tests for src/terminal_theme.py — design-system palette loading."""

from __future__ import annotations

from pathlib import Path

from src.terminal_theme import load_theme


def test_load_theme_reads_design_tokens():
    theme = load_theme()
    # Values come straight from design/tokens.json (references resolved).
    assert theme.accent == "#FF2F70"
    assert theme.interactive == "#8EBEFF"
    assert theme.secondary == "#ACB3D3"
    assert theme.success == "#6DCE43"
    assert theme.warning == "#FF5F00"
    assert theme.error == "#FF2626"
    assert theme.purple == "#A459FF"
    assert theme.text == "#FFFFFF"


def test_load_theme_falls_back_when_tokens_missing(tmp_path: Path):
    theme = load_theme(tmp_path / "does-not-exist.json")
    # The fallback mirrors the current tokens; update both together.
    assert theme.accent == "#FF2F70"
    assert theme.interactive == "#8EBEFF"
    assert theme.error == "#FF2626"


def test_load_theme_falls_back_on_invalid_json(tmp_path: Path):
    bad = tmp_path / "tokens.json"
    bad.write_text("not json")
    assert load_theme(bad).accent == "#FF2F70"
