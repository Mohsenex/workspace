"""Euler-inner-bend spiral PCell for AMF CHiP PDK.

The inner section of the double spiral is two mirrored S-connectors (top and
bottom half-circles), each made from two 90° bends.  Across all four bends:

  Q1 (arm1 side, outer) – circular   ← arm connects here
  Q2 (centre seam)      – Euler      ← curvature-transition point
  Q3 (centre seam)      – Euler      ← curvature-transition point (mirrored)
  Q4 (arm2 side, outer) – circular   ← arm connects here

Default parameters match the requested spec:
  - inner bend radius : 270 µm
  - waveguide width   : 3 µm
  - arm separation    : 6.5 µm
  - target length     : ~17 mm  (≈ 5 loops)
"""

import gdsfactory as gf
from gdsfactory.path import spiral_archimedean
from gdsfactory.typings import CrossSectionSpec

from amf.chp import PDK, LAYER

PDK.activate()


@gf.cell
def spiral_euler(
    min_bend_radius: float = 270.0,
    separation: float = 6.5,
    number_of_loops: float = 4.5,
    width: float = 3.0,
    npoints: int = 10000,
) -> gf.Component:
    """Archimedean double spiral with mixed circular/Euler inner bends.

    The inner S-connector uses four 90° bends across the two half-circles:
      - Q1, Q4 (outer, where spiral arms attach) are plain circular bends.
      - Q2, Q3 (inner, at the curvature-reversal seam)  are Euler bends.

    Args:
        min_bend_radius: Radius of the inner bends (µm).
        separation: Centre-to-centre gap between adjacent spiral arms (µm).
        number_of_loops: Number of loops in each half of the double spiral.
        width: Waveguide width (µm).
        npoints: Path discretisation points for the spiral arms.

    Returns:
        Component with ports o1 and o2 at the outer ends of the spiral.
    """
    xs = gf.cross_section.strip(width=width, layer=LAYER.WG)
    r = min_bend_radius / 2

    circ = gf.get_component(gf.components.bend_circular, radius=r, angle=90, cross_section=xs)
    euler = gf.get_component("bend_euler", radius=r, angle=90, p=1.0, cross_section=xs)

    component = gf.Component()

    # bend1: circular — arm1 attaches here (outer/entry)
    # bend2: Euler    — sits at the centre seam (inner)
    # bend2 is mirrored and its tip (o2) meets bend1's tip (o2) at the seam.
    bend1 = component.add_ref(circ)
    bend2 = component.add_ref(euler)
    bend2.mirror()
    bend2.connect("o2", bend1.ports["o2"])

    # Archimedean spiral arms
    path = spiral_archimedean(
        min_bend_radius=min_bend_radius,
        separation=separation,
        number_of_loops=number_of_loops,
        npoints=npoints,
    )
    path.start_angle = 0
    path.end_angle = 0

    spiral_arm = path.extrude(cross_section=xs)

    arm1 = component.add_ref(spiral_arm)
    arm2 = component.add_ref(spiral_arm)
    arm2.mirror()

    arm1.connect("o1", bend1.ports["o1"], mirror=True)
    arm2.connect("o1", bend2.ports["o1"])

    component.add_port("o1", port=arm1.ports["o2"])
    component.add_port("o2", port=arm2.ports["o2"])

    arm_length = path.length()
    bend_length = circ.info.get("length", 0) + euler.info.get("length", 0)
    total_length = (arm_length + bend_length) * 2
    component.info["length_um"] = float(total_length)
    component.info["length_mm"] = float(total_length / 1000)

    component.flatten()
    return component


if __name__ == "__main__":
    c = spiral_euler()
    print(f"Spiral length: {c.info['length_mm']:.3f} mm")
    c.show()
