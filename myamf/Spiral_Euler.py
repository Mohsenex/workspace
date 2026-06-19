"""Euler-inner-bend spiral PCell for AMF CHiP PDK.

Two mirrored Archimedean spiral arms are joined at the centre by a 180°
U-turn made from two back-to-back 90° Euler bends so that the minimum-
radius section has continuous curvature throughout.

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
    """Archimedean double spiral with Euler inner bends.

    The inner 180° U-turn is formed by two back-to-back 90° Euler bends,
    giving continuous curvature at the tightest point of the spiral.

    Args:
        min_bend_radius: Minimum bend radius of the inner Euler turn (µm).
        separation: Centre-to-centre gap between adjacent spiral arms (µm).
        number_of_loops: Number of loops in each half of the double spiral.
        width: Waveguide width (µm).
        npoints: Path discretisation points for the spiral arms.

    Returns:
        Component with ports o1 and o2 at the outer ends of the spiral.
    """
    xs = gf.cross_section.strip(width=width, layer=LAYER.WG)

    # 90° Euler bend — two of these form the inner 180° U-turn.
    # radius=min_bend_radius/2 so the outer edge reaches min_bend_radius.
    bend_90 = gf.get_component(
        "bend_euler",
        radius=min_bend_radius / 2,
        angle=90,
        cross_section=xs,
    )

    component = gf.Component()

    bend1 = component.add_ref(bend_90)
    bend2 = component.add_ref(bend_90)

    # Place bend2 mirrored and rotated to form the 180° U-turn with bend1.
    # After connecting: o1(bend1) → spiral-arm-1, o2(bend2) → spiral-arm-2.
    bend2.mirror()
    bend2.connect("o2", bend1.ports["o2"])

    # Archimedean spiral arms (same path, mirrored for the return arm)
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

    bend_length = bend_90.info.get("length", 0)
    arm_length = path.length()
    total_length = (arm_length + bend_length) * 2
    component.info["length_um"] = float(total_length)
    component.info["length_mm"] = float(total_length / 1000)

    component.flatten()
    return component


if __name__ == "__main__":
    c = spiral_euler()
    print(f"Spiral length: {c.info['length_mm']:.3f} mm")
    c.show()
