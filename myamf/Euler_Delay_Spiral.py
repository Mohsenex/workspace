import gdsfactory as gf
from gdsfactory.path import Path
import numpy as np


def _spiral_archimedean(
    min_bend_radius: float,
    separation: float,
    number_of_loops: float,
    npoints: int,
) -> Path:
    return Path(
        np.array(
            [
                (separation / np.pi * theta + min_bend_radius)
                * np.array((np.sin(theta), np.cos(theta)))
                for theta in np.linspace(0, number_of_loops * 2 * np.pi, npoints)
            ]
        )
    )


@gf.cell
def _bend_euler_180_two_90(
    radius: float = 10.0,
    cross_section: gf.typings.CrossSectionSpec = "strip",
    # spiral_double passes angle=180 and cross_section — ignore angle, use radius
    angle: float = 180,
) -> gf.Component:
    """180-degree turn from two back-to-back 90-degree fully-Euler bends.

    Stays within its own quadrant footprint so it never cuts into adjacent
    spiral arms — unlike a single 180-degree Euler bend which splays sideways.
    """
    c = gf.Component()
    b1 = c.add_ref(
        gf.get_component(
            "bend_euler", radius=radius, angle=90, p=1.0, cross_section=cross_section
        )
    )
    b2 = c.add_ref(
        gf.get_component(
            "bend_euler", radius=radius, angle=90, p=1.0, cross_section=cross_section
        )
    )
    b2.connect("o1", b1.ports["o2"])
    c.add_port("o1", port=b1.ports["o1"])
    c.add_port("o2", port=b2.ports["o2"])
    return c


@gf.cell
def Euler_Delay_Spiral(
    min_bend_radius: float = 100.0,
    separation: float = 6.5,
    number_of_loops: int = 8,
    npoints: int = 1000,
) -> gf.Component:
    """Double spiral whose innermost bend uses two 90-degree fully-Euler bends.

    Two 90-degree Euler bends replace the single 180-degree Euler bend so that
    the arms do not splay sideways into adjacent spiral loops.
    """
    component = gf.Component()

    bend = gf.get_component(
        _bend_euler_180_two_90,
        radius=min_bend_radius / 2,
        cross_section="nitride",
    )
    bend1 = component.add_ref(bend)
    bend2 = component.add_ref(bend)
    bend2.connect("o2", bend1.ports["o1"], mirror=True)

    path = _spiral_archimedean(
        min_bend_radius=min_bend_radius,
        separation=separation,
        number_of_loops=number_of_loops,
        npoints=npoints,
    )
    path.start_angle = 0
    path.end_angle = 0

    spiral = path.extrude(cross_section="nitride")
    spiral1 = component.add_ref(spiral)
    spiral2 = component.add_ref(spiral)
    spiral2.mirror()

    spiral2.connect("o1", bend2.ports["o1"])
    spiral1.connect("o1", bend1.ports["o2"], mirror=True)

    component.add_port("o1", port=spiral1.ports["o2"])
    component.add_port("o2", port=spiral2.ports["o2"])
    return component
