"""Booth-Layout MCP server.

Exposes floor-plan + booth layout as MCP tools so an AI assistant (Claude, or any
MCP client) can build and arrange a trade-show floor from natural language:
"a 100×80 hall, 6 rows of 10 booths at 8×8 ft with 6 ft cross-aisles, VIP row of 5
along the top wall" → real geometry, bounds-checked and overlap-validated, exported
to SVG or JSON.

Run:  python server.py           # stdio MCP server (add to your client's mcpServers)
State persists to booth_plan.json between tool calls.
"""
import os

from mcp.server.fastmcp import FastMCP

from boothlayout import FloorPlan
from boothlayout import layout as L
from boothlayout import render

STATE = os.environ.get("BOOTH_PLAN", "booth_plan.json")
mcp = FastMCP("booth-layout")


def _load():
    return FloorPlan.load(STATE) if os.path.exists(STATE) else FloorPlan()


def _save(plan):
    plan.save(STATE)


@mcp.tool()
def create_floor(name: str = "Show Floor", width: float = 100, height: float = 80) -> dict:
    """Start a fresh floor plan of the given size (feet). Clears any existing plan."""
    plan = FloorPlan(name, width, height)
    _save(plan)
    return {"ok": True, "plan": {"name": name, "width": width, "height": height}}


@mcp.tool()
def add_booth(x: float, y: float, w: float, h: float, label: str = "", vendor: str = "") -> dict:
    """Add one booth at (x,y) with size w×h feet. Returns the new booth id and
    whether it's in bounds / overlapping anything."""
    plan = _load()
    b = plan.add(x, y, w, h, label, vendor)
    ok = plan.in_bounds(b)
    _save(plan)
    return {"id": b.id, "in_bounds": ok, "overlaps": L.overlaps(plan)}


@mcp.tool()
def grid(rows: int, cols: int, booth_w: float, booth_h: float,
         aisle: float = 6.0, aisle_every: int = 2, gap: float = 0.0,
         margin: float = 4.0, prefix: str = "B") -> dict:
    """Lay out rows×cols booths with a wider cross-aisle after every `aisle_every`
    rows. Out-of-bounds booths are skipped. Returns count placed + stats."""
    plan = _load()
    made = L.grid(plan, rows, cols, booth_w, booth_h, aisle, aisle_every, gap, margin, prefix=prefix)
    _save(plan)
    return {"placed": len(made), "ids": [b.id for b in made], "stats": L.stats(plan)}


@mcp.tool()
def along_wall(side: str, count: int, booth_w: float, booth_h: float,
               gap: float = 0.0, margin: float = 2.0, prefix: str = "W") -> dict:
    """Place `count` booths along a wall: 'top' | 'bottom' | 'left' | 'right'."""
    plan = _load()
    made = L.along_wall(plan, side, count, booth_w, booth_h, gap, margin, prefix)
    _save(plan)
    return {"placed": len(made), "ids": [b.id for b in made]}


@mcp.tool()
def assign_vendor(booth_id: int, vendor: str) -> dict:
    """Assign a vendor/exhibitor to a booth."""
    plan = _load()
    b = plan.get(booth_id)
    if not b:
        return {"ok": False, "error": f"no booth {booth_id}"}
    b.vendor = vendor
    _save(plan)
    return {"ok": True, "booth": booth_id, "vendor": vendor}


@mcp.tool()
def move_booth(booth_id: int, x: float, y: float) -> dict:
    """Move a booth to a new (x,y). Reports if it now overlaps or leaves bounds."""
    plan = _load()
    b = plan.get(booth_id)
    if not b:
        return {"ok": False, "error": f"no booth {booth_id}"}
    b.x, b.y = x, y
    _save(plan)
    return {"ok": True, "in_bounds": plan.in_bounds(b), "overlaps": L.overlaps(plan)}


@mcp.tool()
def list_booths() -> dict:
    """List every booth with position, size, and assigned vendor."""
    plan = _load()
    return {"name": plan.name, "size": [plan.width, plan.height],
            "booths": [b.__dict__ for b in plan.booths]}


@mcp.tool()
def validate() -> dict:
    """Check the plan: overlapping pairs, out-of-bounds booths, and utilization."""
    plan = _load()
    oob = [b.id for b in plan.booths if not plan.in_bounds(b)]
    return {"overlaps": L.overlaps(plan), "out_of_bounds": oob, "stats": L.stats(plan)}


@mcp.tool()
def export_svg(path: str = "floor.svg") -> dict:
    """Render the current plan to an SVG file for review."""
    plan = _load()
    with open(path, "w") as f:
        f.write(render.to_svg(plan))
    return {"ok": True, "path": path, "stats": L.stats(plan)}


if __name__ == "__main__":
    mcp.run()
