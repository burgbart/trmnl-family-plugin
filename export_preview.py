"""Export a static preview.html showing every device's Liquid-rendered dashboard.

Renders each configured device profile (src/config.py) that has a real
template via src/liquid_render.py, then writes a single static preview.html
with one tab per device. Each device's rendered HTML is embedded in its own
<iframe srcdoc="..."> — the device templates emit full self-contained
stylesheets (og.liquid a <style> block, x.liquid a full <!doctype html>
document), so concatenating their raw HTML into one page would cause CSS
rules from one device to bleed into another (duplicate `.box`/`.page`
selectors, differing @font-face, etc). An iframe with srcdoc gives each
device its own document/style scope, avoiding that collision entirely, while
still working as a single static file (no server, no external requests).

Usage:
    python export_preview.py [--input PATH] [--output PATH]
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from src.config import _DEVICE_PROFILES
from src.liquid_render import render

_DEFAULT_INPUT = Path("templates/dummy_dashboard.json")
_DEFAULT_OUTPUT = Path("preview.html")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render every device's Liquid template into one static preview.html."
    )
    parser.add_argument(
        "--input",
        default=str(_DEFAULT_INPUT),
        help=f"Path to a dashboard.json file (default: {_DEFAULT_INPUT}).",
    )
    parser.add_argument(
        "--output",
        default=str(_DEFAULT_OUTPUT),
        help=f"Path to write the static preview HTML (default: {_DEFAULT_OUTPUT}).",
    )
    return parser.parse_args()


def _grayscale_filter_css(levels: int) -> str:
    """Return a CSS `filter` value approximating a device's grayscale levels.

    Every device gets `grayscale(1)` (removes hue/saturation, matching an
    e-ink panel's single luminance channel). A low level count (e.g. OG's
    1-bit/2-level panel) additionally gets `contrast()` pushed up to
    approximate hard black/white thresholding — full posterization isn't
    expressible with a plain CSS filter, but a strong contrast boost is a
    reasonable visual approximation without a canvas/SVG step.
    """
    if levels <= 2:
        return "grayscale(1) contrast(4.5)"
    if levels <= 4:
        return "grayscale(1) contrast(2.2)"
    if levels <= 8:
        return "grayscale(1) contrast(1.4)"
    return "grayscale(1)"


def build_preview_html(data: dict, device_names: list[str] | None = None) -> str:
    """Render every device with a template and compose the tabbed preview page.

    Args:
        data: Parsed dashboard.json payload.
        device_names: Optional slugs (e.g. ["og"]) to restrict which device
            profiles are rendered. Defaults to every profile with a template.
    """
    devices = [p for p in _DEVICE_PROFILES.values() if p.template_filename is not None]
    if device_names is not None:
        devices = [p for p in devices if p.name in device_names]
    if not devices:
        raise RuntimeError("No device profiles with a template found; nothing to preview.")

    tabs: list[str] = []
    panels: list[str] = []
    for i, profile in enumerate(devices):
        rendered_html = render(profile, data)
        active = " active" if i == 0 else ""
        tabs.append(
            f'<button class="tab{active}" data-target="frame-{profile.name}" '
            f'type="button">{html.escape(profile.name.upper())} '
            f'<span class="tab-dims">{profile.width}×{profile.height}</span></button>'
        )
        filter_css = _grayscale_filter_css(profile.grayscale_levels)
        panels.append(
            f"""
      <div class="panel{active}" id="panel-{profile.name}">
        <div class="frame-meta">
          {html.escape(profile.name.upper())} &mdash; {profile.width}&times;{profile.height}px,
          {profile.grayscale_levels}-level grayscale approximation
        </div>
        <div class="frame-scale-wrap">
          <iframe
            id="frame-{profile.name}"
            class="device-frame"
            style="width:{profile.width}px; height:{profile.height}px; filter:{filter_css};"
            srcdoc="{html.escape(rendered_html, quote=True)}"
            scrolling="no"
          ></iframe>
        </div>
      </div>"""
        )

    tabs_html = "\n      ".join(tabs)
    panels_html = "".join(panels)

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>TRMNL Dashboard Preview</title>
<style>
  :root {{
    color-scheme: light dark;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 24px;
    font-family: -apple-system, "Segoe UI", Arial, sans-serif;
    background: #1e1e1e;
    color: #eee;
  }}
  h1 {{
    font-size: 18px;
    font-weight: 600;
    margin: 0 0 16px;
  }}
  .tabs {{
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
    flex-wrap: wrap;
  }}
  .tab {{
    background: #2c2c2c;
    color: #ddd;
    border: 1px solid #444;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 14px;
    cursor: pointer;
  }}
  .tab:hover {{
    background: #3a3a3a;
  }}
  .tab.active {{
    background: #4a90d9;
    border-color: #4a90d9;
    color: #fff;
  }}
  .tab-dims {{
    opacity: 0.7;
    font-size: 12px;
    margin-left: 4px;
  }}
  .panel {{
    display: none;
  }}
  .panel.active {{
    display: block;
  }}
  .frame-meta {{
    font-size: 13px;
    color: #aaa;
    margin-bottom: 8px;
  }}
  .frame-scale-wrap {{
    background: #000;
    display: inline-block;
    padding: 1px;
    max-width: 100%;
    overflow: auto;
  }}
  .device-frame {{
    display: block;
    border: none;
  }}
</style>
</head>
<body>
  <h1>TRMNL Dashboard Preview</h1>
  <div class="tabs">
      {tabs_html}
  </div>
  {panels_html}
  <script>
    (function () {{
      var tabs = document.querySelectorAll('.tab');
      tabs.forEach(function (tab) {{
        tab.addEventListener('click', function () {{
          var target = tab.getAttribute('data-target');
          document.querySelectorAll('.tab').forEach(function (t) {{
            t.classList.remove('active');
          }});
          document.querySelectorAll('.panel').forEach(function (p) {{
            p.classList.remove('active');
          }});
          tab.classList.add('active');
          document.getElementById('panel-' + target.replace('frame-', '')).classList.add('active');
        }});
      }});
    }})();
  </script>
</body>
</html>
"""


def main() -> None:
    args = _parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    data = json.loads(input_path.read_text(encoding="utf-8"))
    preview_html = build_preview_html(data)

    output_path.write_text(preview_html, encoding="utf-8")
    print(f"Wrote preview to {output_path} (from {input_path})")


if __name__ == "__main__":
    main()
