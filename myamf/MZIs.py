import gdsfactory as gf
from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_Si2X2MMI_Cband_v5p0,
)


@gf.cell
def MZIs(
    arm1_length: float = 50.0,
    arm2_length: float = 100.0,
    gap: float = 100.0,
    cross_section: str = "strip",
    straight: str = "straight",
    bend: str = "bend_euler",
) -> gf.Component:
    """Mach-Zehnder Interferometer with configurable arm lengths.

    Args:
        arm1_length: Length of the top arm straight section (µm).
        arm2_length: Length of the bottom arm straight section (µm).
        gap: Distance between the east face of the splitter and
             the west face of the combiner (µm).
        cross_section: Waveguide cross-section for arms and bends.
        straight: Straight waveguide component to use for arms.
        bend: Bend component to use for routing arms.

    Ports:
        o1: optical input (west, from 1x2 MMI)
        o2: optical output top (east, from 2x2 MMI)
        o3: optical output bottom (east, from 2x2 MMI)
    """
    c = gf.Component()

    # --- Place splitter at origin ---
    splitter = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    combiner = c.add_ref(AMF_300LSOI_Si2X2MMI_Cband_v5p0())

    # Position combiner so its west face (o1/o2 ports) is exactly `gap` µm
    # east of the splitter's east face (o2/o3 ports).
    splitter_xmax = splitter.ports["o2"].center[0]
    combiner_xmin = combiner.ports["o1"].center[0]
    combiner.movex(splitter_xmax + gap - combiner_xmin)

    # Align combiner vertically with splitter
    combiner.movey(splitter.ports["o2"].center[1] - combiner.ports["o2"].center[1])

    # --- Route arms between splitter outputs and combiner inputs ---
    # Top arm: splitter.o3 → combiner.o1
    gf.routing.route_single(
        c,
        port1=splitter.ports["o3"],
        port2=combiner.ports["o1"],
        bend=bend,
        cross_section=cross_section,
        straight=straight,
    )
    # Bottom arm: splitter.o2 → combiner.o2
    gf.routing.route_single(
        c,
        port1=splitter.ports["o2"],
        port2=combiner.ports["o2"],
        bend=bend,
        cross_section=cross_section,
        straight=straight,
    )

    # --- Expose ports ---
    c.add_port("o1", port=splitter.ports["o1"])   # input
    c.add_port("o2", port=combiner.ports["o4"])   # top output
    c.add_port("o3", port=combiner.ports["o3"])   # bottom output

    return c
