"""Measurements in pixel-scaled image space or estimated 3D space."""
from dataclasses import dataclass
import math

import numpy as np


@dataclass(frozen=True)
class Features:
    # Index, middle, ring and little finger, in anatomical order.
    pip: tuple[float, ...]
    dip: tuple[float, ...]
    index_base: float
    thumb_ip: float
    thumb_direction: float
    thumb_index_gap: float
    thumb_palm_gap: float
    spread: float


def calculate_angle(a, b, c):
    """Interior angle ABC in degrees, or None for unusable segments."""
    try:
        points = np.asarray((a, b, c), dtype=float)
    except (ValueError, TypeError):
        return None
    if points.shape not in ((3, 2), (3, 3)) or not np.isfinite(points).all():
        return None
    u, v = points[0] - points[1], points[2] - points[1]
    lengths = np.linalg.norm((u, v), axis=1)
    if lengths.min() <= 1e-9:
        return None
    cosine = np.dot(u / lengths[0], v / lengths[1])
    return math.degrees(math.acos(np.clip(cosine, -1.0, 1.0)))


def extract(points):
    """Measure one hand in consistent Cartesian units. Reject collapsed palms."""
    try:
        p = np.asarray(points, dtype=float)
    except (ValueError, TypeError):
        return None
    if p.shape not in ((21, 2), (21, 3)) or not np.isfinite(p).all():
        return None

    def distance(i, j):
        return float(np.linalg.norm(p[i] - p[j]))

    width = distance(5, 17)
    length = distance(0, 9)
    if min(width, length) <= 1e-9 or width < 0.15 * length:
        return None
    # Use palm-width units before checking bone lengths, across image sizes.
    p = (p - p[0]) / width
    bases = (5, 9, 13, 17)
    bones = [(start, start + 1) for base in (1, *bases)
             for start in range(base, base + 3)]
    if any(distance(i, j) < 0.015 for i, j in bones):
        return None
    pip = tuple(calculate_angle(*p[i:i+3]) for i in bases)
    dip = tuple(calculate_angle(*p[i+1:i+4]) for i in bases)
    base = calculate_angle(*p[[0, 5, 6]])
    ip = calculate_angle(*p[[2, 3, 4]])
    direction = calculate_angle(*p[[4, 2, 9]])
    if None in (*pip, *dip, base, ip, direction):
        return None
    return Features(pip, dip, base, ip, direction, distance(4, 8),
                    distance(4, 9), distance(8, 12))


def image_points(landmarks, width, height, depth=False):
    """Scale normalized x/y and, optionally, model-relative z into image units."""
    if depth:
        return [(p.x * width, p.y * height, p.z * width) for p in landmarks]
    return [(p.x * width, p.y * height) for p in landmarks]
