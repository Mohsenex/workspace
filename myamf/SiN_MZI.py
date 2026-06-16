import gdsfactory as gf
from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_Si2X2MMI_Cband_v5p0,
    AMF_300LSOI_LSiN2SOISSC_Cband_v5p0,
)


@gf.cell
def SiN_MZI(
    gap: float = 300,
    dl: float = 17.470,
    cross_section: str = "strip",
) -> gf.Component:
    """MZI with two rectangular arms using explicit gf.Path quarter arcs.

    Upper arm (reference, +Y):
        → 15 µm east
        ↑ arc +90° (turn north)
        ↑ 20 µm north
        → arc -90° (turn east)
        → middle horizontal straight
        ↓ arc -90° (turn south)
        ↓ 20 µm south
        → arc +90° (turn east)
        → remaining straight to combiner o1

    Lower arm (longer by dl, -Y): same shape mirrored downward,
    with extra length added to the vertical legs to achieve dl.
    """
    c = gf.Component()
    xs = gf.get_cross_section(cross_section)
    R = xs.radius

    # ------------------------------------------------------------------ #
    # MMI placement                                                        #
    # ------------------------------------------------------------------ #
    splitter = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    combiner = c.add_ref(AMF_300LSOI_Si2X2MMI_Cband_v5p0())

    # Place combiner gap µm east of splitter (port face to port face)
    combiner.movex(
        splitter.ports["o2"].center[0] + gap - combiner.ports["o1"].center[0]
    )

    #-------------------------------------------------------
    # Via Placement
    #-------------------------------------------------------
    via_up1 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via_up1.move([55 + 2*R, 2*R + 0.9])

    via_up2 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via_up2.mirror_x()
    via_up2.move([242 + 55 + 2*R, 2*R + 0.9])


    via_bottom1 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via_bottom1.move([55 + 2*R, - (2*R + 0.9) - dl/2])

    via_bottom2 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via_bottom2.mirror_x()
    via_bottom2.move([242 + 55 + 2*R + dl, -(2*R + 0.9) - dl/2])

    #---------------------------------------------------------------------
    # Routing
    #---------------------------------------------------------------------
    # Upper arm:
    r1 = gf.routing.route_single(
        c,
        port1=splitter.ports["o2"],
        port2=via_up1.ports["o1"],
        cross_section=cross_section,
    )
    r2 = gf.routing.route_single(
        c,
        port1=via_up2.ports["o1"],
        port2=combiner.ports["o2"],
        cross_section=cross_section,
    )

    # Routing for the lower arm:
    r3 = gf.routing.route_single(
        c,
        port1=splitter.ports["o3"],
        port2=via_bottom1.ports["o1"],
        cross_section=cross_section,
    )
    r4 = gf.routing.route_single(
        c,
        port1=via_bottom2.ports["o1"],
        port2=combiner.ports["o1"],
        cross_section=cross_section,
    )

    # SiN section:
    r5 = gf.routing.route_single(
        c,
        port1=via_bottom1.ports["o2"],
        port2=via_bottom2.ports["o2"],
        cross_section='nitride',
    )

    #----- Ports----------------------
    term = c.add_ref(gf.components.terminator(doping_layers=[]))
    term.connect('o1', combiner.ports['o3'])

    c.add_port('o1', port = splitter.ports['o1'])
    c.add_port('o2', port = combiner.ports['o4'])

    return c
