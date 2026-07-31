"""Terminal color theme aligned with the design system in ``design/``.

Rich accepts truecolor hex styles, so the terminal dashboard can use the
exact palette from ``design/tokens.json``. Values are loaded from that file
at import time; when it is unavailable (e.g. an installed copy without the
``design/`` folder), a fallback mirroring the tokens is used — keep the
fallback in sync when tokens change.

Note on color choices: the terminal controls its own background and font, so
only foreground colors map over. Brand navy (#0A1A65) and brand blue
(#0065FE) are too dark to read on dark terminal backgrounds, which is why
interactive values use the dark-theme interactive color (blue-light #8EBEFF).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

TOKENS_PATH = Path(__file__).resolve().parent.parent / "design" / "tokens.json"


@dataclass(frozen=True)
class TerminalTheme:
    text: str  # default foreground
    secondary: str  # muted captions/metadata (supplements rich's "dim")
    accent: str  # brand pink — highlights
    interactive: str  # times, links, active values
    purple: str  # differentiation (anniversaries)
    success: str  # done, refreshed
    warning: str  # alerts, due soon
    error: str  # errors, overdue


_FALLBACK = TerminalTheme(
    text="#FFFFFF",
    secondary="#ACB3D3",
    accent="#FF2F70",
    interactive="#8EBEFF",
    purple="#A459FF",
    success="#6DCE43",
    warning="#FF5F00",
    error="#FF2626",
)


def _resolve(tokens: dict, value: object) -> str:
    """Resolve a DTCG ``{path.to.token}`` reference to its ``$value``."""
    if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
        node = tokens
        for part in value[1:-1].split("."):
            node = node[part]
        return _resolve(tokens, node["$value"])
    return str(value)


def load_theme(path: Path = TOKENS_PATH) -> TerminalTheme:
    """Load the terminal palette from ``design/tokens.json``."""
    try:
        tokens = json.loads(path.read_text(encoding="utf-8"))
        color = tokens["color"]
        dark = tokens["theme"]["dark"]
        return TerminalTheme(
            text=_resolve(tokens, color["surface"]["base"]["$value"]),
            secondary=_resolve(tokens, color["text"]["secondary"]["$value"]),
            accent=_resolve(tokens, color["brand"]["pink"]["$value"]),
            interactive=_resolve(tokens, dark["interactive"]["$value"]),
            purple=_resolve(tokens, color["brand"]["purple"]["$value"]),
            success=_resolve(tokens, color["semantic"]["success"]["$value"]),
            warning=_resolve(tokens, color["semantic"]["warning"]["$value"]),
            error=_resolve(tokens, color["semantic"]["error"]["$value"]),
        )
    except (OSError, KeyError, json.JSONDecodeError, TypeError):
        return _FALLBACK


THEME = load_theme()
