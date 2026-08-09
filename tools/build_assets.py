#!/usr/bin/env python3
"""Generate the banner and panel SVGs for the profile README.

Run:  python3 tools/build_assets.py

Everything the README shows as artwork is produced here and committed to the
repo, so nothing depends on a third-party image service that can rate-limit,
change, or disappear.

Constraints these files are built against (verified against GitHub, not assumed):
  * raw.githubusercontent.com serves SVG under
    `default-src 'none'; style-src 'unsafe-inline'; sandbox`
    -> an inline <style> block and CSS animation work; scripts, external fonts
       and external images do not. Every font here is a system stack.
  * Inline <svg> inside markdown is stripped by GitHub's sanitizer, so artwork
    has to be a committed .svg referenced by <img>.
  * <picture> + prefers-color-scheme survives sanitizing; GitHub wraps it in its
    own <themed-picture> element and drives it from the GitHub theme setting.

Animation rule: the resting state of every element is the finished design, and
each reveal is staggered through keyframe percentages on one shared timeline
rather than through animation-delay + fill-mode. If the animation never runs,
the artwork is still complete rather than blank.
"""

import datetime
import os
import xml.dom.minidom

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), 'assets')

# ── identity tokens ────────────────────────────────────────────────────────────
# Change ACCENT in one place to re-brand every asset.
THEMES = {
    'light': dict(ink='#1F2328', ink2='#59636E', ink3='#8C959F',
                  line='#D0D7DE', accent='#BC5B12'),
    'dark':  dict(ink='#E6EDF3', ink2='#9198A1', ink3='#636C76',
                  line='#3D444D', accent='#F0A93B'),
}

MONO = ('ui-monospace,SFMono-Regular,&#34;SF Mono&#34;,Menlo,Consolas,'
        '&#34;Liberation Mono&#34;,monospace')
SANS = ('-apple-system,BlinkMacSystemFont,&#34;Segoe UI&#34;,&#34;Noto Sans&#34;,'
        'Helvetica,Arial,sans-serif')

CAREER_START = datetime.date(2019, 11, 1)   # IFS R&D, first role
TIMELINE = 1.9                              # shared animation length, seconds


def years_experience(today=None):
    today = today or datetime.date.today()
    return (today - CAREER_START).days // 365


def esc(s):
    """XML-escape text content. Everything user-facing must go through this --
    a bare '&' silently produces a malformed file that renders as a broken image."""
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


class Reveal:
    """Staggered keyframes on one shared timeline.

    Deliberately emits no animation-delay and no fill-mode: the element's own
    style is the finished state, and the keyframes only hold it back at the
    start. Nothing is ever hidden by a fill-mode that outlives the animation.
    """

    def __init__(self):
        self._frames = []

    def at(self, from_state, start, dur=.5):
        name = f'r{len(self._frames) + 1}'
        pct = max(0.0, min(100.0, start / TIMELINE * 100))
        self._frames.append(f'@keyframes {name}{{0%,{pct:.1f}%{{{from_state}}}}}')
        return f'animation:{name} {TIMELINE}s cubic-bezier(.22,.9,.25,1)'

    def css(self):
        return '\n  '.join(self._frames)


def document(body, css, width, height, label):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-label="{esc(label)}">\n'
        f'<title>{esc(label)}</title>\n'
        f'<style>\n{css}\n'
        f'  @media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}\n'
        f'</style>\n{body}\n</svg>\n'
    )


# ── banner ─────────────────────────────────────────────────────────────────────
def banner(t):
    r = Reveal()
    width, height = 1200, 340

    # Column positions are fixed rather than measured: system font metrics differ
    # per platform, so nothing here may depend on the rendered width of a string.
    meta = [('LEAD SOFTWARE ENGINEER', 70), ('ALTRIUM', 500),
            ('SINCE 2019', 744), ('COLOMBO, LK', 964)]

    cells = ''.join(
        f'<text class="meta" x="{x}" y="274" '
        f'style="{r.at("opacity:0;transform:translateY(8px)", .55 + .09 * i, .5)}">'
        f'{esc(label)}</text>'
        for i, (label, x) in enumerate(meta))

    rules = ''.join(
        f'<line x1="{x - 22}" y1="252" x2="{x - 22}" y2="280" stroke="{t["line"]}"/>'
        for _, x in meta[1:])

    css = f'''  .name{{font-family:{SANS};font-size:152px;font-weight:250;
        fill:{t['ink']};letter-spacing:-5px}}
  .stop{{fill:{t['accent']}}}
  .meta{{font-family:{MONO};font-size:19px;fill:{t['ink2']};letter-spacing:2.6px}}
  .tag{{font-family:{MONO};font-size:18px;fill:{t['ink3']};letter-spacing:3px}}
  .hair{{stroke:{t['line']};stroke-width:1}}
  {r.css()}'''

    body = f'''
  <text class="tag" x="70" y="62" style="{r.at('opacity:0', .05, .4)}">THARINDA RAJAPAKSHA</text>
  <text class="tag" x="1130" y="62" text-anchor="end"
        style="{r.at('opacity:0', .08, .4)}">SOFTWARE ENGINEERING</text>
  <line class="hair" x1="70" y1="90" x2="1130" y2="90"
        style="{r.at('stroke-dasharray:0 1100', .12, .85)}"/>
  <text class="name" x="60" y="214"
        style="{r.at('opacity:0;transform:translateY(12px)', .26, .6)}">Tharinda<tspan
        class="stop">.</tspan></text>
  <line class="hair" x1="70" y1="248" x2="1130" y2="248"
        style="{r.at('stroke-dasharray:0 1100', .2, .85)}"/>
  {rules}{cells}'''

    return document(body, css, width, height, 'Tharinda — Lead Software Engineer')


# ── panel ──────────────────────────────────────────────────────────────────────
def panel(t):
    r = Reveal()
    width, height = 1200, 120
    yrs = years_experience()

    columns = [
        ('EXPERIENCE', [f'{yrs}+ years', '4 companies']),
        ('CORE',       ['Java  ·  Spring Boot', 'C++  ·  Kubernetes  ·  AWS']),
        ('DOMAINS',    ['Payments & billing', 'Capital markets  ·  ERP']),
    ]

    out, x = '', 44
    for i, (heading, lines) in enumerate(columns):
        out += (f'<text class="h" x="{x}" y="34" '
                f'style="{r.at("opacity:0", .05 + .1 * i, .45)}">{esc(heading)}</text>')
        for k, line in enumerate(lines):
            out += (f'<text class="v" x="{x}" y="{68 + k * 26}" '
                    f'style="{r.at("opacity:0", .12 + .1 * i + .05 * k, .45)}">'
                    f'{esc(line)}</text>')
        if i < len(columns) - 1:
            out += (f'<line x1="{x + 330}" y1="18" x2="{x + 330}" y2="104" '
                    f'stroke="{t["line"]}"/>')
        x += 372

    css = f'''  text{{font-family:{MONO}}}
  .h{{font-size:14px;fill:{t['ink3']};letter-spacing:2.6px}}
  .v{{font-size:17px;fill:{t['ink2']}}}
  {r.css()}'''

    body = (f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="10" '
            f'fill="none" stroke="{t["line"]}"/>'
            f'<rect x="1" y="1" width="5" height="{height - 2}" fill="{t["accent"]}"/>'
            + out)

    return document(body, css, width, height,
                    f'{yrs}+ years across 4 companies. Java, Spring Boot, C++, '
                    f'Kubernetes, AWS. Payments and billing, capital markets, ERP.')


def main():
    os.makedirs(ASSETS, exist_ok=True)
    for theme, tokens in THEMES.items():
        for name, render in (('banner', banner), ('panel', panel)):
            path = os.path.join(ASSETS, f'{name}-{theme}.svg')
            with open(path, 'w') as fh:
                fh.write(render(tokens))
            # Parse it back: a malformed SVG renders as a broken image on GitHub
            # with no other warning, so fail here instead of shipping it.
            try:
                xml.dom.minidom.parse(path)
            except Exception as exc:
                raise SystemExit(f'malformed SVG {path}: {exc}')
            print(f'  {os.path.relpath(path, os.path.dirname(HERE))}'
                  f'  {os.path.getsize(path):,} bytes')


if __name__ == '__main__':
    main()
