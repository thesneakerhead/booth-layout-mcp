"""Exercise the layout core directly (no MCP client needed) and write an SVG.

    python examples/demo.py   # -> writes spring-expo.svg
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from boothlayout import FloorPlan
from boothlayout import layout as L
from boothlayout import render

plan = FloorPlan("Spring Expo", width=80, height=60)

# main field: 8 rows × 5 cols of 8×8 booths, 6 ft cross-aisle every 2 rows
main = L.grid(plan, rows=8, cols=5, booth_w=8, booth_h=8, aisle=6, aisle_every=2)

# sponsor row along the top wall
L.along_wall(plan, side="bottom", count=4, booth_w=10, booth_h=8, prefix="S")

# assign a few vendors
for bid, name in [(1, "Acme"), (2, "Globex"), (3, "Initech")]:
    b = plan.get(bid)
    if b:
        b.vendor = name

print("stats:", L.stats(plan))
print("overlaps:", L.overlaps(plan))

with open("spring-expo.svg", "w") as f:
    f.write(render.to_svg(plan))
print("wrote spring-expo.svg")
