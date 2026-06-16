import gdsfactory as gf
from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_Si2X2MMI_Cband_v5p0,
    AMF_300LSOI_LSiN2SOISSC_Cband_v5p0,
)


@gf.cell
def via_test(
    arm_length: float = 200.0,
    gap: float = 100.0,
    cross_section: str = "strip",
    bend: str = "bend_euler",
) -> gf.Component:
    """MZI with equal-length arms where one arm passes through a Si→SiN→Si via pair.

    The two vias (Si-to-SiN and SiN-to-Si) are placed back-to-back in the
    middle of the top arm.  Both arms have identical optical path length so
    that any phase difference is due solely to the via pair.

    Args:
        arm_length: Total straight-waveguide length budget for each arm (µm).
            The via pair occupies some of this budget; the remaining length is
            split equally as Si straights on either side of the vias.
        gap: Distance (µm) between the east face of the splitter and the west
             face of the combiner.
        cross_section: Si waveguide cross-section used for the arms and bends.
        bend: Bend component name used when routing arms.

    Ports:
        o1: optical input  (west, splitter)
        o2: optical output top    (east, combiner)
        o3: optical output bottom (east, combiner)
    """
    c = gf.Component()

    # ------------------------------------------------------------------ #
    # Fixed cells                                                          #
    # ------------------------------------------------------------------ #
    splitter = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    combiner = c.add_ref(AMF_300LSOI_Si2X2MMI_Cband_v5p0())

    # Position combiner: its input ports are `gap` µm east of the splitter
    # output ports.
    splitter_xmax = splitter.ports["o2"].center[0]
    combiner_xmin = combiner.ports["o1"].center[0]
    combiner.movex(splitter_xmax + gap - combiner_xmin)

    # Align combiner vertically so the two MMIs share the same centre-line.
    combiner.movey(
        splitter.ports["o2"].center[1] - combiner.ports["o2"].center[1]
    )

    # ------------------------------------------------------------------ #
    # Bottom arm (reference): plain Si straight                           #
    # ------------------------------------------------------------------ #
    gf.routing.route_single(
        c,
        port1=splitter.ports["o2"],
        port2=combiner.ports["o2"],
        bend=bend,
        cross_section=cross_section,
        straight="straight",
    )

    # ------------------------------------------------------------------ #
    # Top arm (via arm): Si — [Si→SiN via]—[SiN→Si via] — Si             #
    #                                                                      #
    # Via pair geometry:                                                   #
    #   via_fwd  : o1(Si, W) ──▶ o2(SiN, E)                              #
    #   via_rev  : o2(SiN, W) ◀── o1(Si, E)   (mirrored about Y-axis)    #
    #   connected: via_fwd.o2 (SiN) joined to via_rev.o2 (SiN)           #
    #                                                                      #
    # The combined Si→SiN→Si sub-component is placed at the centre of the #
    # top arm and the remaining Si length is split on both sides.          #
    # ------------------------------------------------------------------ #

    # Build the via sub-component once so we can measure its longitudinal extent.
    _via_single = AMF_300LSOI_LSiN2SOISSC_Cband_v5p0()
    _c_o2 = _via_single.ports["o2"].center
    _c_o1 = _via_single.ports["o1"].center
    via_width = float(_c_o2[0]) - float(_c_o1[0])  # longitudinal extent of one via

    via_pair_width = 2 * via_width  # two vias back-to-back

    # Si straight half-length on each side of the via pair.
    # We ensure a minimum of 1 µm to avoid zero-length straights.
    si_half = max((arm_length - via_pair_width) / 2.0, 1.0)

    # --- Place via pair (free-standing sub-component) ---
    # via_fwd: Si(W) → SiN(E)
    via_fwd = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())

    # via_rev: mirror of via_fwd so its SiN port faces West (touching via_fwd.o2)
    via_rev = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via_rev.mirror_x()  # flip horizontally: o2(SiN) is now on the West side

    # Connect SiN ports: move via_rev so its o2 coincides with via_fwd.o2
    fwd_o2 = via_fwd.ports["o2"].center
    rev_o2 = via_rev.ports["o2"].center
    via_rev.move((fwd_o2[0] - rev_o2[0], fwd_o2[1] - rev_o2[1]))

    # The via pair now exposes:
    #   via_fwd.o1  — Si input  (West)
    #   via_rev.o1  — Si output (East)

    # --- Route top arm in three segments ---
    # Segment 1: splitter.o3  →  via_fwd.o1   (Si straight + bends)
    gf.routing.route_single(
        c,
        port1=splitter.ports["o3"],
        port2=via_fwd.ports["o1"],
        bend=bend,
        cross_section=cross_section,
        straight="straight",
    )

    # Segment 2: via_rev.o1  →  combiner.o1   (Si straight + bends)
    gf.routing.route_single(
        c,
        port1=via_rev.ports["o1"],
        port2=combiner.ports["o1"],
        bend=bend,
        cross_section=cross_section,
        straight="straight",
    )

    # ------------------------------------------------------------------ #
    # Expose top-level ports                                               #
    # ------------------------------------------------------------------ #
    c.add_port("o1", port=splitter.ports["o1"])   # optical input
    c.add_port("o2", port=combiner.ports["o4"])   # top output
    c.add_port("o3", port=combiner.ports["o3"])   # bottom output

    return c
