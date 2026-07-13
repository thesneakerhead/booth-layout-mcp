---
name: booth-layout
description: Design and validate a trade-show / vending-event floor plan from a natural-language brief, using the booth-layout MCP tools. Use when someone wants to lay out booths, assign vendors, check aisles/overlaps, or export a floor map.
---

# Booth Layout

Turn a floor brief into a concrete, valid booth layout using the `booth-layout`
MCP tools, then hand back an SVG the organizer can review.

## Workflow

1. **Pin the hall + rules.** Get (or assume, and state) the hall size in feet,
   booth size, number of booths, and aisle width. Fire-code aisles are typically
   ≥ 6 ft; keep a perimeter margin.
2. **Start the floor:** `create_floor(name, width, height)`.
3. **Bulk-place the field:** `grid(rows, cols, booth_w, booth_h, aisle, aisle_every)`
   for the main hall. Use `aisle_every=2` for back-to-back "pod" rows with a shared
   aisle every two rows. Add feature booths with `along_wall(side, count, …)` (e.g.
   a sponsor row along `top`).
4. **Always `validate()`** after placing. If `overlaps` or `out_of_bounds` is
   non-empty, fix it: shrink booths, widen aisles, or `move_booth(...)`. Never hand
   back a plan that fails validation.
5. **Assign vendors** the organizer names with `assign_vendor(booth_id, vendor)`.
6. **Export:** `export_svg("floor.svg")` and summarize the stats (booth count,
   utilization %, aisle width) back to the user.

## Judgment

- Prefer fewer, wider aisles over cramming — utilization above ~55–60% usually
  means aisles are too tight; say so.
- If the brief doesn't fit the hall, place what fits, report how many were dropped,
  and suggest a smaller booth size or a bigger hall — don't silently overflow.
- Keep booth sizes consistent within a section unless asked otherwise.

## Example brief → actions

> "80×60 hall, 40 booths at 8×8, double rows with 6 ft aisles, plus 4 sponsor
> booths along the top."

```
create_floor("Spring Expo", 80, 60)
grid(rows=8, cols=5, booth_w=8, booth_h=8, aisle=6, aisle_every=2)
along_wall(side="top", count=4, booth_w=10, booth_h=8, prefix="S")
validate()            # fix anything flagged
export_svg("spring-expo.svg")
```
