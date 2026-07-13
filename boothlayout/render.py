"""Render a FloorPlan to SVG so layouts are reviewable at a glance — assigned
booths are filled, empty booths outlined, labels centered.
"""
from . import layout as _layout


def to_svg(plan, scale=8, pad=20):
    W = plan.width * scale + pad * 2
    H = plan.height * scale + pad * 2
    overlapping = {i for pair in _layout.overlaps(plan) for i in pair}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" '
        f'viewBox="0 0 {W:.0f} {H:.0f}" font-family="system-ui,sans-serif">',
        f'<rect x="{pad}" y="{pad}" width="{plan.width*scale:.0f}" height="{plan.height*scale:.0f}" '
        f'fill="#f8fafc" stroke="#0f172a" stroke-width="2"/>',
    ]
    for b in plan.booths:
        x, y = pad + b.x * scale, pad + b.y * scale
        w, h = b.w * scale, b.h * scale
        if b.id in overlapping:
            fill, stroke = "#fecaca", "#dc2626"
        elif b.vendor:
            fill, stroke = "#bfdbfe", "#2563eb"
        else:
            fill, stroke = "#ffffff", "#94a3b8"
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
                     f'fill="{fill}" stroke="{stroke}" stroke-width="1.5" rx="2"/>')
        text = b.vendor or b.label
        if text and w > 18:
            parts.append(f'<text x="{x + w/2:.1f}" y="{y + h/2 + 3:.1f}" text-anchor="middle" '
                         f'font-size="{min(11, w/4):.0f}" fill="#0f172a">{_esc(text)[:14]}</text>')
    parts.append(f'<text x="{pad}" y="{pad-6}" font-size="13" fill="#334155">{_esc(plan.name)}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def _esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
