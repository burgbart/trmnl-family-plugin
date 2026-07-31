"""Guards for the design system in ``design/``.

Three things can silently rot in a design system, and each has a test here:

1. **Dangling references** — a token pointing at a token path that no longer exists.
2. **Mirror drift** — ``design/index.html`` re-declares the palette as CSS custom
   properties so the style guide needs no build step. Nothing but this test stops
   the two files from disagreeing.
3. **Contrast regressions** — a "nicer" hex quietly dropping a prescribed
   text/background pair below WCAG AA.

The CSS variable -> token path mapping below is the contract. Adding a
``--color-*`` or ``--gradient-*`` custom property to the style guide without a
token to back it fails ``test_no_unmapped_color_variables``.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

DESIGN_DIR = Path(__file__).resolve().parent.parent / "design"
TOKENS_PATH = DESIGN_DIR / "tokens.json"
STYLE_GUIDE_PATH = DESIGN_DIR / "index.html"

# --- CSS custom property -> token path -------------------------------------

LIGHT_VARS = {
    "--color-pink": "color.brand.pink",
    "--color-pink-deep": "color.brand.pink-deep",
    "--color-navy": "color.brand.navy",
    "--color-blue": "color.brand.blue",
    "--color-blue-light": "color.brand.blue-light",
    "--color-purple": "color.brand.purple",
    "--color-purple-dark": "color.brand.purple-dark",
    "--color-surface": "color.surface.base",
    "--color-surface-tinted": "color.surface.tinted",
    "--color-card": "color.surface.base",
    "--color-text-primary": "color.text.primary",
    "--color-text-muted": "color.text.muted",
    "--color-text-secondary": "color.text.secondary",
    "--color-text-inverse": "color.text.inverse",
    "--color-border": "color.border.subtle",
    "--color-border-strong": "color.border.strong",
    "--color-focus": "color.focus.ring",
    "--color-interactive": "color.brand.blue",
    "--color-success": "color.semantic.success",
    "--color-success-surface": "color.semantic.success-surface",
    "--color-success-text": "color.semantic.success-text",
    "--color-success-bright": "color.semantic.success-bright",
    "--color-warning": "color.semantic.warning",
    "--color-warning-surface": "color.semantic.warning-surface",
    "--color-warning-text": "color.semantic.warning-text",
    "--color-error": "color.semantic.error",
    "--color-error-surface": "color.semantic.error-surface",
    "--color-error-text": "color.semantic.error-text",
    "--color-info": "color.semantic.info",
    "--color-info-surface": "color.semantic.info-surface",
    "--color-info-text": "color.semantic.info-text",
    "--color-accent-surface": "color.semantic.accent-surface",
    "--color-accent-text": "color.semantic.accent-text",
    "--color-purple-surface": "color.semantic.purple-surface",
    "--color-purple-text": "color.semantic.purple-text",
    "--gradient-cta": "color.gradient.cta",
    "--gradient-blue": "color.gradient.blue",
}

DARK_VARS = {
    "--color-surface": "theme.dark.surface.base",
    "--color-surface-tinted": "theme.dark.surface.tinted",
    "--color-card": "theme.dark.surface.raised",
    "--color-text-primary": "theme.dark.text.primary",
    "--color-text-muted": "theme.dark.text.muted",
    "--color-border": "theme.dark.border",
    "--color-border-strong": "theme.dark.border-strong",
    "--color-focus": "color.focus.ring-dark",
    "--color-interactive": "theme.dark.interactive",
    "--color-success-surface": "theme.dark.semantic.success-surface",
    "--color-success-text": "theme.dark.semantic.success-text",
    "--color-warning-surface": "theme.dark.semantic.warning-surface",
    "--color-warning-text": "theme.dark.semantic.warning-text",
    "--color-error-surface": "theme.dark.semantic.error-surface",
    "--color-error-text": "theme.dark.semantic.error-text",
    "--color-info-surface": "theme.dark.semantic.info-surface",
    "--color-info-text": "theme.dark.semantic.info-text",
    "--color-accent-surface": "theme.dark.semantic.accent-surface",
    "--color-accent-text": "theme.dark.semantic.accent-text",
    "--color-purple-surface": "theme.dark.semantic.purple-surface",
    "--color-purple-text": "theme.dark.semantic.purple-text",
}

# Custom properties in the dark block that are deliberately not tokens: on dark
# surfaces the blue-tinted shadows read as haze, so the style guide neutralises
# them. Documented in the CSS with the same reasoning.
DERIVED_DARK_VARS = {"--shadow-card", "--shadow-raised"}

# --- Prescribed contrast pairs ---------------------------------------------
# (foreground token, background token, minimum ratio, label)
#
# 4.5 = WCAG 2.1 AA for body text (1.4.3); 3.0 = AA for large/bold text and for
# non-text UI boundaries (1.4.11).

LIGHT_PAIRS = [
    ("color.text.primary", "color.surface.base", 4.5, "body text on base"),
    ("color.text.primary", "color.surface.tinted", 4.5, "body text on tinted band"),
    ("color.text.muted", "color.surface.base", 4.5, "muted text on base"),
    ("color.text.muted", "color.surface.tinted", 4.5, "muted text on tinted band"),
    ("color.brand.blue", "color.surface.base", 4.5, "link on base"),
    ("color.semantic.info-text", "color.surface.tinted", 4.5, "link on tinted band"),
    ("color.semantic.success-text", "color.semantic.success-surface", 4.5, "success badge"),
    ("color.semantic.success-text", "color.surface.base", 4.5, "success text on base"),
    ("color.semantic.warning-text", "color.semantic.warning-surface", 4.5, "warning badge"),
    ("color.semantic.warning-text", "color.surface.base", 4.5, "warning text on base"),
    ("color.semantic.error-text", "color.semantic.error-surface", 4.5, "error badge"),
    ("color.semantic.error-text", "color.surface.base", 4.5, "error text on base"),
    ("color.semantic.info-text", "color.semantic.info-surface", 4.5, "info badge"),
    ("color.semantic.info-text", "color.surface.base", 4.5, "info text on base"),
    ("color.semantic.accent-text", "color.semantic.accent-surface", 4.5, "accent badge"),
    ("color.semantic.accent-text", "color.surface.base", 4.5, "accent text on base"),
    ("color.semantic.purple-text", "color.semantic.purple-surface", 4.5, "purple badge"),
    ("color.semantic.purple-text", "color.surface.base", 4.5, "purple text on base"),
    ("color.text.inverse", "color.brand.pink", 3.0, "CTA label (large/bold only)"),
    ("color.border.strong", "color.surface.base", 3.0, "input border on base"),
    ("color.border.strong", "color.surface.tinted", 3.0, "input border on tinted band"),
    ("color.focus.ring", "color.surface.base", 3.0, "focus ring on base"),
    ("color.focus.ring", "color.surface.tinted", 3.0, "focus ring on tinted band"),
    # Navy bands keep their own foregrounds in both themes.
    ("color.text.inverse", "color.brand.navy", 4.5, "heading on navy band"),
    ("color.text.secondary", "color.brand.navy", 4.5, "body text on navy band"),
    ("color.brand.blue-light", "color.brand.navy", 4.5, "link on navy band"),
]

DARK_PAIRS = [
    ("theme.dark.text.primary", "theme.dark.surface.base", 4.5, "body text on dark base"),
    ("theme.dark.text.primary", "theme.dark.surface.raised", 4.5, "body text on dark card"),
    ("theme.dark.text.muted", "theme.dark.surface.base", 4.5, "muted text on dark base"),
    ("theme.dark.text.muted", "theme.dark.surface.raised", 4.5, "muted text on dark card"),
    ("theme.dark.text.muted", "theme.dark.surface.tinted", 4.5, "muted text on dark band"),
    ("theme.dark.interactive", "theme.dark.surface.base", 4.5, "link on dark base"),
    ("theme.dark.interactive", "theme.dark.surface.raised", 4.5, "link on dark card"),
    ("theme.dark.semantic.success-text", "theme.dark.semantic.success-surface", 4.5, "dark success badge"),
    ("theme.dark.semantic.success-text", "theme.dark.surface.raised", 4.5, "dark success on card"),
    ("theme.dark.semantic.warning-text", "theme.dark.semantic.warning-surface", 4.5, "dark warning badge"),
    ("theme.dark.semantic.warning-text", "theme.dark.surface.raised", 4.5, "dark warning on card"),
    ("theme.dark.semantic.error-text", "theme.dark.semantic.error-surface", 4.5, "dark error badge"),
    ("theme.dark.semantic.error-text", "theme.dark.surface.raised", 4.5, "dark error on card"),
    ("theme.dark.semantic.info-text", "theme.dark.semantic.info-surface", 4.5, "dark info badge"),
    ("theme.dark.semantic.info-text", "theme.dark.surface.raised", 4.5, "dark info on card"),
    ("theme.dark.semantic.accent-text", "theme.dark.semantic.accent-surface", 4.5, "dark accent badge"),
    ("theme.dark.semantic.accent-text", "theme.dark.surface.raised", 4.5, "dark accent on card"),
    ("theme.dark.semantic.purple-text", "theme.dark.semantic.purple-surface", 4.5, "dark purple badge"),
    ("theme.dark.semantic.purple-text", "theme.dark.surface.raised", 4.5, "dark purple on card"),
    ("theme.dark.border-strong", "theme.dark.surface.base", 3.0, "dark input border"),
    ("theme.dark.border-strong", "theme.dark.surface.raised", 3.0, "dark input border on card"),
    ("color.focus.ring-dark", "theme.dark.surface.base", 3.0, "dark focus ring"),
    ("color.focus.ring-dark", "theme.dark.surface.raised", 3.0, "dark focus ring on card"),
]


# --- Helpers ---------------------------------------------------------------


@pytest.fixture(scope="module")
def tokens() -> dict:
    return json.loads(TOKENS_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def style_guide() -> str:
    return STYLE_GUIDE_PATH.read_text(encoding="utf-8")


def _lookup(tokens: dict, path: str) -> dict:
    node = tokens
    for part in path.split("."):
        assert part in node, f"token path {path!r} does not exist (missing {part!r})"
        node = node[part]
    return node


def resolve(tokens: dict, path: str) -> str:
    """Resolve a token path to its final value, following ``{a.b.c}`` references."""
    value = _lookup(tokens, path)["$value"]
    seen = {path}
    while isinstance(value, str) and value.startswith("{") and value.endswith("}"):
        ref = value[1:-1]
        assert ref not in seen, f"circular token reference at {path!r}"
        seen.add(ref)
        value = _lookup(tokens, ref)["$value"]
    return str(value)


def resolve_inline(tokens: dict, value: str) -> str:
    """Resolve every ``{a.b.c}`` reference embedded in a string (e.g. gradients)."""
    return re.sub(
        r"\{([^}]+)\}",
        lambda m: resolve(tokens, m.group(1)),
        value,
    )


def iter_tokens(node, path=""):
    """Yield ``(path, token_dict)`` for every leaf token."""
    if not isinstance(node, dict):
        return
    if "$value" in node:
        yield path, node
        return
    for key, child in node.items():
        if key.startswith("$"):
            continue
        yield from iter_tokens(child, f"{path}.{key}" if path else key)


def _css_block(style_guide: str, selector: str) -> dict[str, str]:
    """Extract ``--name: value;`` declarations from the first block of a selector."""
    start = style_guide.index(selector + " {")
    end = style_guide.index("\n  }", start)
    block = style_guide[start:end]
    return {
        name: value.strip()
        for name, value in re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", block)
    }


def _srgb_channel(value: float) -> float:
    value /= 255
    return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4


def parse_color(value: str) -> tuple[float, float, float, float]:
    value = value.strip()
    match = re.fullmatch(r"#([0-9a-fA-F]{6})", value)
    if match:
        digits = match.group(1)
        return (*(int(digits[i : i + 2], 16) for i in (0, 2, 4)), 1.0)
    match = re.fullmatch(r"rgba?\(([^)]+)\)", value)
    if match:
        parts = [float(p) for p in re.split(r"[,\s/]+", match.group(1).strip()) if p]
        alpha = parts[3] if len(parts) > 3 else 1.0
        return (parts[0], parts[1], parts[2], alpha)
    raise AssertionError(f"cannot parse color {value!r}")


def contrast_ratio(foreground: str, background: str) -> float:
    """WCAG 2.1 contrast ratio; translucent foregrounds composite over the background."""
    fr, fg, fb, alpha = parse_color(foreground)
    br, bg, bb, _ = parse_color(background)
    if alpha < 1:
        fr = fr * alpha + br * (1 - alpha)
        fg = fg * alpha + bg * (1 - alpha)
        fb = fb * alpha + bb * (1 - alpha)

    def luminance(r, g, b):
        return 0.2126 * _srgb_channel(r) + 0.7152 * _srgb_channel(g) + 0.0722 * _srgb_channel(b)

    lighter, darker = sorted(
        [luminance(fr, fg, fb), luminance(br, bg, bb)], reverse=True
    )
    return (lighter + 0.05) / (darker + 0.05)


# --- Tests: token file integrity -------------------------------------------


def test_tokens_parse_and_are_typed(tokens):
    leaves = list(iter_tokens(tokens))
    assert len(leaves) >= 100, "token file looks truncated"
    untyped = [path for path, token in leaves if "$type" not in token]
    assert untyped == [], f"tokens missing $type: {untyped}"


def test_no_dangling_references(tokens):
    for path, token in iter_tokens(tokens):
        value = token["$value"]
        if not isinstance(value, str):
            continue
        for ref in re.findall(r"\{([^}]+)\}", value):
            node = tokens
            for part in ref.split("."):
                assert part in node, f"{path} references missing token {{{ref}}}"
                node = node[part]
            assert "$value" in node, f"{path} references group {{{ref}}}, not a token"


def test_version_metadata_present(tokens):
    meta = tokens["$extensions"]["com.trmnl-home.meta"]
    assert re.fullmatch(r"\d+\.\d+\.\d+", meta["version"])
    assert meta["styleGuide"] == "design/index.html"
    assert meta["syncGuard"] == "tests/test_design_tokens.py"


# --- Tests: style guide mirrors the tokens ---------------------------------


@pytest.mark.parametrize("var,path", sorted(LIGHT_VARS.items()))
def test_light_css_variables_match_tokens(tokens, style_guide, var, path):
    declared = _css_block(style_guide, ":root")
    assert var in declared, f"{var} missing from :root in index.html"
    expected = resolve_inline(tokens, _lookup(tokens, path)["$value"])
    assert declared[var].lower() == expected.lower(), (
        f"{var} in index.html is {declared[var]!r} but {path} resolves to {expected!r}"
    )


@pytest.mark.parametrize("var,path", sorted(DARK_VARS.items()))
def test_dark_css_variables_match_tokens(tokens, style_guide, var, path):
    declared = _css_block(style_guide, '[data-theme="dark"]')
    assert var in declared, f"{var} missing from the dark block in index.html"
    expected = resolve_inline(tokens, _lookup(tokens, path)["$value"])
    assert declared[var].lower() == expected.lower(), (
        f"{var} in the dark block is {declared[var]!r} but {path} resolves to {expected!r}"
    )


def test_no_unmapped_color_variables(style_guide):
    """Every colour custom property must be backed by a token."""
    light = {v for v in _css_block(style_guide, ":root") if v.startswith(("--color", "--gradient"))}
    assert light - set(LIGHT_VARS) == set(), "unmapped colour variables in :root"

    dark = {
        v
        for v in _css_block(style_guide, '[data-theme="dark"]')
        if v.startswith(("--color", "--gradient"))
    }
    assert dark - set(DARK_VARS) - DERIVED_DARK_VARS == set(), (
        "unmapped colour variables in the dark block"
    )


def test_dark_block_overrides_only_known_variables(style_guide):
    declared = set(_css_block(style_guide, '[data-theme="dark"]'))
    assert declared <= set(DARK_VARS) | DERIVED_DARK_VARS


# --- Tests: accessibility ---------------------------------------------------


@pytest.mark.parametrize(
    "fg,bg,minimum,label", LIGHT_PAIRS, ids=[p[3] for p in LIGHT_PAIRS]
)
def test_light_theme_contrast(tokens, fg, bg, minimum, label):
    ratio = contrast_ratio(resolve(tokens, fg), resolve(tokens, bg))
    assert ratio >= minimum, f"{label}: {fg} on {bg} is {ratio:.2f}:1, needs {minimum}:1"


@pytest.mark.parametrize(
    "fg,bg,minimum,label", DARK_PAIRS, ids=[p[3] for p in DARK_PAIRS]
)
def test_dark_theme_contrast(tokens, fg, bg, minimum, label):
    ratio = contrast_ratio(resolve(tokens, fg), resolve(tokens, bg))
    assert ratio >= minimum, f"{label}: {fg} on {bg} is {ratio:.2f}:1, needs {minimum}:1"


def test_text_secondary_is_documented_as_dark_only(tokens):
    """The trap this release exists to close: #ACB3D3 is 2.07:1 on white."""
    assert contrast_ratio(resolve(tokens, "color.text.secondary"), "#FFFFFF") < 3.0
    description = _lookup(tokens, "color.text.secondary")["$description"]
    assert "DARK surfaces only" in description
    assert "never use it on a light surface" in description


def test_solid_state_fills_are_not_prescribed_for_white_text(tokens):
    """Documents why badges use the -surface/-text pair instead of solid fills."""
    for state in ("success", "warning", "error"):
        solid = resolve(tokens, f"color.semantic.{state}")
        assert contrast_ratio("#FFFFFF", solid) < 4.5
        surface = resolve(tokens, f"color.semantic.{state}-surface")
        text = resolve(tokens, f"color.semantic.{state}-text")
        assert contrast_ratio(text, surface) >= 4.5


# --- Tests: style guide markup ---------------------------------------------


def test_style_guide_has_accessibility_affordances(style_guide):
    assert 'class="skip-link"' in style_guide and 'href="#main"' in style_guide
    assert ":focus-visible" in style_guide
    assert "prefers-reduced-motion" in style_guide
    assert 'id="main"' in style_guide


def test_style_guide_is_responsive(style_guide):
    assert "max-width: 900px" in style_guide
    assert "max-width: 600px" in style_guide
    assert "clamp(" in style_guide


def test_hero_token_count_fallback_is_accurate(tokens, style_guide):
    """The style guide advertises a token count; it must be the real one."""
    match = re.search(r'id="stat-tokens" data-fallback="(\d+)"', style_guide)
    assert match, "hero token-count stat is missing its data-fallback"
    assert int(match.group(1)) == len(list(iter_tokens(tokens)))


def test_style_guide_sections_are_linked_from_the_nav(style_guide):
    nav = style_guide[style_guide.index('class="secnav"') : style_guide.index("</nav>")]
    for href in re.findall(r'href="#([a-z-]+)"', nav):
        assert f'id="{href}"' in style_guide, f"nav links to #{href} but no section has that id"
