"""Floor-plan + booth model. Units are feet; the origin (0,0) is the top-left of
the hall. A booth is an axis-aligned rectangle with an optional assigned vendor.
Plans serialize to plain JSON so they're easy to store, diff, and hand to a UI.
"""
import json
from dataclasses import asdict, dataclass, field


@dataclass
class Booth:
    id: int
    x: float
    y: float
    w: float
    h: float
    label: str = ""
    vendor: str = ""

    @property
    def rect(self):
        return (self.x, self.y, self.x + self.w, self.y + self.h)

    def overlaps(self, other, gap=0.0):
        ax0, ay0, ax1, ay1 = self.rect
        bx0, by0, bx1, by1 = other.rect
        return not (ax1 + gap <= bx0 or bx1 + gap <= ax0 or ay1 + gap <= by0 or by1 + gap <= ay0)


@dataclass
class FloorPlan:
    name: str = "Show Floor"
    width: float = 100.0
    height: float = 80.0
    booths: list = field(default_factory=list)
    _next_id: int = 1

    def add(self, x, y, w, h, label="", vendor=""):
        b = Booth(self._next_id, float(x), float(y), float(w), float(h), label, vendor)
        self.booths.append(b)
        self._next_id += 1
        return b

    def get(self, booth_id):
        for b in self.booths:
            if b.id == booth_id:
                return b
        return None

    def remove(self, booth_id):
        n = len(self.booths)
        self.booths = [b for b in self.booths if b.id != booth_id]
        return len(self.booths) != n

    def in_bounds(self, b):
        return 0 <= b.x and 0 <= b.y and b.x + b.w <= self.width and b.y + b.h <= self.height

    def to_dict(self):
        d = asdict(self)
        d["booths"] = [asdict(b) for b in self.booths]
        return d

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, d):
        fp = cls(d.get("name", "Show Floor"), d.get("width", 100), d.get("height", 80))
        for b in d.get("booths", []):
            fp.booths.append(Booth(**b))
        fp._next_id = max([b.id for b in fp.booths], default=0) + 1
        return fp

    @classmethod
    def load(cls, path):
        with open(path) as f:
            return cls.from_dict(json.load(f))

    def save(self, path):
        with open(path, "w") as f:
            f.write(self.to_json())
