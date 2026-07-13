# booth-layout-mcp

**An MCP server that lets an AI assistant design a trade-show / vending-event floor
plan from plain language** — place booths, keep fire-code aisles, assign vendors,
validate for overlaps and out-of-bounds, and export an SVG map. Ships with a Claude
**skill** so "lay out my show floor" just works.

> "100×80 hall, 6 rows of 10 booths at 8×8 ft with 6 ft cross-aisles, plus a
> sponsor row of 5 along the top wall" → a validated floor plan + `floor.svg`.

## Why

Event organizers describe a floor in words; turning that into correct geometry
(consistent booths, legal aisles, nothing overlapping, nothing off the edge) is
fiddly and error-prone by hand. This exposes the layout engine as **MCP tools**, so
a model can do the placement and — crucially — **validate** it, while a human stays
in charge of vendor assignments and final sign-off.

## What's in it

| Piece | Role |
|---|---|
| `server.py` | MCP server (FastMCP) exposing the tools below over stdio. |
| `boothlayout/model.py` | `FloorPlan` + `Booth` geometry; JSON serialization. |
| `boothlayout/layout.py` | `grid`, `along_wall`, overlap detection, utilization stats. |
| `boothlayout/render.py` | Floor plan → SVG (assigned booths filled, collisions flagged red). |
| `skills/booth-layout/SKILL.md` | A Claude skill that drives the tools from a brief. |

### Tools

`create_floor` · `add_booth` · `grid` · `along_wall` · `assign_vendor` ·
`move_booth` · `list_booths` · `validate` · `export_svg`

Every placement is **bounds-checked** (booths outside the hall are dropped) and
`validate()` reports overlapping pairs, out-of-bounds booths, and floor utilization —
so the model can self-correct before returning a plan.

## Run it

```bash
pip install -r requirements.txt

# try the engine directly (no MCP client) — writes an SVG you can open:
python examples/demo.py

# run as an MCP server (stdio):
python server.py
```

Register it with any MCP client (e.g. Claude Desktop / Claude Code):

```json
{
  "mcpServers": {
    "booth-layout": { "command": "python", "args": ["/path/to/booth-layout-mcp/server.py"] }
  }
}
```

Then drop `skills/booth-layout/` into your skills directory and ask:
*"Lay out an 80×60 hall with 40 booths at 8×8, double rows and 6 ft aisles, and a
sponsor row along the top."* The assistant places, validates, and hands back a map.

## Design notes

- **Feet, top-left origin.** One consistent coordinate space keeps geometry and
  fire-code reasoning (aisle widths, perimeter margins) simple.
- **Validation is a first-class tool**, not an afterthought — the value of letting a
  model place booths is only realized if it can also *check* its own work.
- **Plans are plain JSON**, so the same layout drops straight into a web canvas
  editor or a print pipeline.
- **Human-in-the-loop.** The tools build and check geometry; a person still owns
  vendor assignments and approval.

## Tech

Python · [Model Context Protocol](https://modelcontextprotocol.io) (FastMCP) ·
dependency-free geometry/SVG core.

## License

MIT
