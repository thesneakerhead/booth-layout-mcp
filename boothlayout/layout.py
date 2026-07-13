"""Layout algorithms + validation over a FloorPlan. These are what make the MCP
tools useful: an agent describes intent ("6 rows of 10, 3ft booths, 6ft aisles")
and these place the geometry, keep it in bounds, and check for overlaps.
"""


def grid(plan, rows, cols, booth_w, booth_h, aisle=6.0, aisle_every=2, gap=0.0,
         margin=4.0, start_x=None, start_y=None, prefix="B"):
    """Lay out rows×cols booths, inserting a wider cross-aisle after every
    `aisle_every` rows. Returns the list of created booths (bounds permitting)."""
    x0 = margin if start_x is None else start_x
    y = margin if start_y is None else start_y
    created, n = [], plan._next_id
    for r in range(rows):
        x = x0
        for c in range(cols):
            b = plan.add(x, y, booth_w, booth_h, label=f"{prefix}{n}")
            if not plan.in_bounds(b):
                plan.remove(b.id)
            else:
                created.append(b); n += 1
            x += booth_w + gap
        y += booth_h + (aisle if (r + 1) % aisle_every == 0 else gap)
    return created


def along_wall(plan, side, count, booth_w, booth_h, gap=0.0, margin=2.0, prefix="W"):
    """Place `count` booths flush along one wall: 'top' | 'bottom' | 'left' | 'right'."""
    created, n = [], plan._next_id
    for i in range(count):
        if side in ("top", "bottom"):
            x = margin + i * (booth_w + gap)
            y = margin if side == "top" else plan.height - booth_h - margin
        else:
            y = margin + i * (booth_h + gap)
            x = margin if side == "left" else plan.width - booth_w - margin
        b = plan.add(x, y, booth_w, booth_h, label=f"{prefix}{n}")
        if not plan.in_bounds(b):
            plan.remove(b.id)
        else:
            created.append(b); n += 1
    return created


def overlaps(plan, gap=0.0):
    """Return every colliding pair of booth ids (spatial validation)."""
    bs = plan.booths
    return [(bs[i].id, bs[j].id)
            for i in range(len(bs)) for j in range(i + 1, len(bs))
            if bs[i].overlaps(bs[j], gap)]


def stats(plan):
    used = sum(b.w * b.h for b in plan.booths)
    total = plan.width * plan.height
    assigned = sum(1 for b in plan.booths if b.vendor)
    return {"booths": len(plan.booths), "assigned": assigned,
            "floor_sqft": round(total, 1), "booth_sqft": round(used, 1),
            "utilization_pct": round(100 * used / total, 1) if total else 0,
            "overlaps": len(overlaps(plan))}
