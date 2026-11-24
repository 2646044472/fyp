"""Pure ranking and capture-window policy. No image I/O or matcher dependency."""
from dataclasses import dataclass, field
import math

@dataclass(frozen=True)
class Candidate:
    frame_id: int
    captured_s: float
    sharpness: float
    contrast: float
    cx: float             # normalized native frame coordinates
    cy: float
    scale: float          # same normalized ROI scale convention in every frame
    angle_rad: float
    texture: tuple         # short vector from normalized ROI, kept in RAM only

def usable(c):
    return (type(c.frame_id) is int and len(c.texture) >= 3
            and all(math.isfinite(v) for v in (c.captured_s, c.sharpness, c.contrast,
                 c.cx, c.cy, c.scale, c.angle_rad, *c.texture))
            and 0 <= c.cx <= 1 and 0 <= c.cy <= 1
            and c.sharpness > 0 and c.contrast > 0 and c.scale > 0
            and max(c.texture) > min(c.texture))

def angle(a,b):
    return abs((a-b+math.pi)%(2*math.pi)-math.pi)

def pose(a,b):
    mean_scale = math.sqrt(a.scale*b.scale)
    return (math.hypot(a.cx-b.cx,a.cy-b.cy)/mean_scale,
            abs(math.log(a.scale/b.scale)), angle(a.angle_rad,b.angle_rad))

def texture(a,b):
    if len(a.texture) != len(b.texture):
        return None
    mean_a, mean_b = sum(a.texture) / len(a.texture), sum(b.texture) / len(b.texture)
    x = tuple(v - mean_a for v in a.texture)
    y = tuple(v - mean_b for v in b.texture)
    return max(-1,min(1,sum(i*j for i,j in zip(x,y)) /
                math.sqrt(sum(v*v for v in x)*sum(v*v for v in y))))

def plausible(c,a):
    center, scale, tilt = pose(c,a)
    return (center <= .60 and scale <= math.log(1.45) and tilt <= math.radians(24))

def duplicate(c,a):
    if c.frame_id == a.frame_id or abs(c.captured_s-a.captured_s) < .24:
        return True
    center, scale, tilt = pose(c,a)
    similarity = texture(c,a)
    return (similarity is not None and similarity >= .994
            and center <= .11 and scale <= .055 and tilt <= math.radians(4))

def coverage(c,a):
    center, scale, tilt = pose(c,a)
    similarity = texture(c,a)
    # Saturation rewards useful small differences rather than distant frames.
    return (.34*min(1, center/.25) + .25*min(1, scale/.17)
            + .25*min(1, tilt/math.radians(11)) +
            .16*min(1,max(0,1-(similarity if similarity is not None else 1))/.08))


def candidate_exclusion(candidate, selected):
    if not selected or any(item.frame_id == candidate.frame_id for item in selected):
        return None
    anchor = selected[0]
    center, scale, tilt = pose(candidate, anchor)
    if center > .60:
        return "POSITION_OUTSIDE_SET"
    if scale > math.log(1.45):
        return "TOO_CLOSE_TO_CAMERA" if candidate.scale > anchor.scale else "TOO_FAR_FROM_CAMERA"
    if tilt > math.radians(24):
        return "ANGLE_OUTSIDE_SET"
    if any(duplicate(candidate, item) for item in selected):
        return "NEAR_DUPLICATE"
    return "LOWER_RANK"


def select_set(candidates, *, retained=(), count=5, frame_quality=None):
    chosen = list(retained)
    clean = [c for c in candidates if usable(c)]
    if not clean or len(chosen) >= count:
        return tuple(chosen[:count])
    if chosen:
        anchor = chosen[0]
    else:
        # Avoid a very sharp lone outlier becoming the reference. Among
        # roughly equally supported candidates still choose the sharper one.
        neighbors = {c.frame_id: sum(plausible(c,o) for o in clean) for c in clean}
        support = max(neighbors.values())
        anchors = [c for c in clean if neighbors[c.frame_id] >= max(1, support-1)]
        anchor = max(anchors, key=lambda c: (
            frame_quality[c.frame_id] if frame_quality is not None else c.sharpness, c.contrast, -c.frame_id))
        chosen.append(anchor)
    pool = [c for c in clean if plausible(c,anchor)]
    if not pool:
        return tuple(chosen[:count])
    # Score all usable frames relative to this camera; no absolute quality floor.
    sharp = sorted([c.sharpness for c in pool]+[anchor.sharpness])
    contrast = sorted([c.contrast for c in pool]+[anchor.contrast])
    ref_s,ref_c = sharp[len(sharp)//2],contrast[len(contrast)//2]
    compared = {}

    def overlaps(c, other):
        key = tuple(sorted((c.frame_id, other.frame_id)))
        if key not in compared:
            compared[key] = duplicate(c, other)
        return compared[key]

    def choices(selected):
        return [c for c in pool if not any(overlaps(c, other) for other in selected)]

    def score(c, selected):
        quality = (frame_quality[c.frame_id] if frame_quality is not None else
                   .65 * min(1.5, c.sharpness / ref_s) + .35 * min(1.5, c.contrast / ref_c))
        spread = min(coverage(c, other) for other in selected)
        return (.62 * quality + .38 * spread, c.sharpness, c.contrast, -c.frame_id)

    while len(chosen) < count:
        eligible = choices(chosen)
        if eligible:
            chosen.append(max(eligible, key=lambda c: score(c, chosen)))
            continue
        if count < 10:
            break
        # A greedy pick can overlap two otherwise compatible frames.
        # Try exchanging it without moving the anchor or any user-retained pick.
        for index in range(len(chosen) - 1, max(1, len(retained)) - 1, -1):
            fixed = chosen[:index] + chosen[index + 1:]
            ranked = sorted(choices(fixed), key=lambda c: score(c, fixed), reverse=True)
            pair = next(((a, b) for i, a in enumerate(ranked) for b in ranked[i + 1:] if not overlaps(a, b)), None)
            if pair is not None:
                chosen[index:index + 1] = pair
                break
        else:
            break
    return tuple(chosen)


def refine_set(initial, candidates, quality, *, retained=(), alternative=()):
    """Compare complete sets, with a bounded search for beneficial swaps."""
    chosen = tuple(initial)
    fixed_ids = {c.frame_id for c in retained}
    pair_spread = {}
    pair_duplicate = {}

    def pair_key(a, b):
        return tuple(sorted((a.frame_id, b.frame_id)))

    def spread(a, b):
        key = pair_key(a, b)
        if key not in pair_spread:
            pair_spread[key] = coverage(a, b)
        return pair_spread[key]

    def repeated(a, b):
        key = pair_key(a, b)
        if key not in pair_duplicate:
            pair_duplicate[key] = duplicate(a, b)
        return pair_duplicate[key]

    def score(items):
        average_quality = sum(quality[c.frame_id] for c in items) / len(items)
        diversity = sum(min(spread(c, other) for other in items if other != c) for c in items) / len(items)
        return .82 * average_quality + .18 * diversity

    if len(chosen) < 2:
        return chosen
    best_score = score(chosen)
    if len(alternative) == len(chosen):
        alternative_score = score(alternative)
        if alternative_score > best_score:
            chosen, best_score = tuple(alternative), alternative_score
    for _ in range(3):
        best = chosen
        selected_ids = {c.frame_id for c in chosen}
        for index, outgoing in enumerate(chosen):
            if outgoing.frame_id in fixed_ids:
                continue
            others = chosen[:index] + chosen[index + 1:]
            for incoming in candidates:
                if incoming.frame_id in selected_ids or any(repeated(incoming, other) for other in others):
                    continue
                if index == 0:
                    if not all(plausible(other, incoming) for other in others):
                        continue
                elif not plausible(incoming, chosen[0]):
                    continue
                trial = chosen[:index] + (incoming,) + chosen[index + 1:]
                value = score(trial)
                if value > best_score + 1e-9:
                    best, best_score = trial, value
        if best is chosen:
            break
        chosen = best
    return (chosen[0], *sorted(chosen[1:], key=lambda c: (-quality[c.frame_id], c.frame_id)))

@dataclass
class Window:
    started_s: float
    absolute_timeout_s: float = 59
    useful_window_s: float = 12
    retained: tuple = ()
    latest_consumed_id: int = -1
    target_count: int = 5
    wait_for_deadline: bool = False
    pool: list = field(default_factory=list, init=False)
    first_valid_s: float|None = field(default=None, init=False)
    _sealed: tuple|None = field(default=None, init=False)
    _ranked: tuple|None = field(default=None, init=False)

    def __post_init__(self):
        if not (math.isfinite(self.started_s)
                and 0 < self.useful_window_s <= self.absolute_timeout_s <= 60):
            raise ValueError("Invalid capture window; never exceed one minute.")
        if not 1 <= self.target_count <= 12 or len(self.retained) > self.target_count or not all(usable(c) for c in self.retained):
            raise ValueError("Invalid retained descriptors.")
        self.latest_consumed_id = max([self.latest_consumed_id]+[c.frame_id for c in self.retained])

    @property
    def deadline(self):
        return self.started_s+self.absolute_timeout_s

    def picks(self):
        if self._ranked is None:
            self._ranked = select_set(self.pool, retained=self.retained, count=self.target_count)
        return self._ranked

    def observe(self,c,now):
        if self._sealed is not None or not math.isfinite(now) or now >= self.deadline:
            return self.status(now)
        if c.frame_id<=self.latest_consumed_id:
            return self.status(now)
        self.latest_consumed_id=c.frame_id
        if usable(c) and self.started_s<=c.captured_s<=now:
            if self.first_valid_s is None:
                self.first_valid_s=now
            if len(self.pool) >= 24:
                protected = self.picks()
                discard = next(item for item in self.pool if item not in protected)
                self.pool.remove(discard)
            self.pool.append(c)
            self._ranked = None
        return self.status(now)

    def status(self,now):
        if not math.isfinite(now):
            raise ValueError("Monotonic time is required.")
        if self._sealed is None:
            selected = self.picks()
            enough = len(selected) == self.target_count
            # Bootstrap with several opportunities, not simply the first five.
            matured = self.first_valid_s is not None and now >= self.first_valid_s + self.useful_window_s
            if now >= self.deadline or (not self.wait_for_deadline and enough and (len(self.pool) >= 12 or matured)):
                self._sealed=selected
            else:
                return "collecting", selected
        return ("ready" if len(self._sealed) == self.target_count else "partial"),self._sealed

    def stop(self,now):
        """Seal at the current time, without waiting for an existing capture."""
        self.status(now)
        if self._sealed is None:
            self._sealed = self.picks()
        return self.status(now)

    def fill_missing(self,now):
        state, chosen = self.status(now)
        if state != "partial":
            raise ValueError("Only a completed partial window can be resumed.")
        return Window(now, self.absolute_timeout_s, self.useful_window_s, chosen, self.latest_consumed_id,
                      self.target_count, self.wait_for_deadline)
