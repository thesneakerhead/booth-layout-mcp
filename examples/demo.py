"""Exercise the layout core directly (no MCP client needed) and write an SVG.

    python examples/demo.py   # -> writes spring-expo.svg
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from boothlayout import FloorPlan
from boothlayout import layout as L
from boothlayout import render

plan = FloorPlan("Spring Expo", width=100, height=70)

# sponsor row along the top wall (10×8 booths)
L.along_wall(plan, side="top", count=6, booth_w=10, booth_h=8, prefix="S")

# main field below the sponsors: 5 rows × 8 cols of 8×8 booths, 6 ft cross-aisle
# every 2 rows, starting under the sponsor row.
L.grid(plan, rows=5, cols=8, booth_w=8, booth_h=8, aisle=6, aisle_every=2, start_y=14)

# assign a few vendors
for bid, name in [(1, "Acme"), (7, "Globex"), (8, "Initech")]:
    b = plan.get(bid)
    if b:
        b.vendor = name

print("stats:", L.stats(plan))
print("overlaps:", L.overlaps(plan), "(empty == valid)")

with open("spring-expo.svg", "w") as f:
    f.write(render.to_svg(plan))
print("wrote spring-expo.svg")
