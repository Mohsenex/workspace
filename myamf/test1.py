import math

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec


@gf.cell(tags=["waveguides"])
def test1(
    radius: float = 10.0,
    total_length: float = 0.0,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """Snake S-bend: two racetrack halves joined together.

    Layout (like a racetrack cut in half and attached):

        o1 (west) --s1-- bend1 (arcs right) --s2-- bend2 (arcs right) --s3-- o2 (west)

    o1 and o2 share the same x position but are offset in y by 4 * radius.

    The natural arc length is 2 * pi * radius (two semicircles). If total_length
    is greater than this, the extra is distributed evenly across the three
    horizontal straight sections (1/4 start, 1/2 middle, 1/4 end).

    Args:
        radius: Bend radius of each semicircle (µm).
        total_length: Desired total path length (µm). Extra beyond 2*pi*radius
            is split across the three straight sections.
        cross_section: Waveguide cross-section spec.
    """
    c = gf.Component()

    # Natural arc length of two 180° circular bends
    natural_length = 2 * math.pi * radius

    # Distribute extra length across the 3 straight sections
    extra = max(0.0, total_length - natural_length)
    l_start  = extra / 4   # straight before bend1  (s1)
    l_middle = extra / 2   # straight between bends  (s2)
    l_end    = extra / 4   # straight after bend2    (s3)

    bend = gf.components.bend_circular(
        radius=radius, angle=180, cross_section=cross_section
    )

    # --- s1: bottom-left horizontal straight ---
    if l_start > 0:
        s1 = c.add_ref(gf.components.straight(length=l_start, cross_section=cross_section))
    else:
        s1 = None

    # --- bend1: arcs to the right at the bottom, from y=0 up to y=2*radius ---
    bend1 = c.add_ref(bend)
    if s1:
        bend1.connect("o1", s1.ports["o2"])
    # else bend1 stays at origin

    # --- s2: middle horizontal straight, connecting bend1 top to bend2 top ---
    if l_middle > 0:
        s2 = c.add_ref(gf.components.straight(length=l_middle, cross_section=cross_section))
        s2.connect("o2", bend1.ports["o2"])
    else:
        s2 = None

    # --- bend2: arcs to the right at the top, from y=2*radius down to y=4*radius ---
    # bend2 is rotated 180° so it arcs rightward but spans downward (from its o1 to o2)
    # After drotate(180): o1 faces east(0), o2 faces east(0), arc goes left.
    # connect o1 to the west-facing end of s2 (or bend1.o2 if no s2).
    bend2 = c.add_ref(bend)
    bend2.drotate(180)
    if s2:
        bend2.connect("o1", s2.ports["o1"])
    else:
        bend2.connect("o1", bend1.ports["o2"])

    # --- s3: top-right horizontal straight ---
    if l_end > 0:
        s3 = c.add_ref(gf.components.straight(length=l_end, cross_section=cross_section))
        s3.connect("o1", bend2.ports["o2"])

    # --- Expose ports ---
    # o1: left end of s1 (or bend1.o1 if no s1)
    if s1:
        c.add_port("o1", port=s1.ports["o1"])
    else:
        c.add_port("o1", port=bend1.ports["o1"])

    # o2: right end of s3 (or bend2.o2 if no s3)
    if l_end > 0:
        c.add_port("o2", port=s3.ports["o2"])
    else:
        c.add_port("o2", port=bend2.ports["o2"])

    return c
