import gdsfactory as gf
import numpy as np
from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_Si2X2MMI_Cband_v5p0,
    AMF_300LSOI_LSiN2SOISSC_Cband_v5p0,
)

@gf.cell
def via_MZI(
    gap: float = 242,
    cross_section: str = "strip",
)->gf.Component:
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
        cross_section=cross_section,        
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


    # --- Place via pair (free-standing sub-component) ---
    # via_fwd: Si(W) → SiN(E)
    via_fwd = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    r = -4*(gap/2/2/np.pi)
    via_fwd.move([55, float(r)])

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

    #-----------------------------------------------------------------------------
    # connect the vias to the splitter and combiner
    #-----------------------------------------------------------------------------
    # Route splitter.o3 → via_fwd.o1 with a target length of gap/2.
    # First measure the natural (minimum) route length, then pad with
    # start/end straights so the total reaches the target.
    target_length = gap / 2
    _probe = gf.Component()
    _r = gf.routing.route_single(
        _probe,
        port1=splitter.ports["o3"],
        port2=via_fwd.ports["o1"],
        cross_section=cross_section,
    )
    natural_length = _r.length
    extra = max(target_length - natural_length, 0.0)
    final_route = gf.routing.route_single(
        c,
        port1=splitter.ports["o3"],
        port2=via_fwd.ports["o1"],
        cross_section=cross_section,
        start_straight_length=extra / 2,
        end_straight_length=extra / 2,
    )
    print(f"[via_MZI] splitter.o3 → via_fwd.o1 route length: {final_route.length:.3f} µm")

    # Route via_rev.o1 → combiner.o1 with the same target length.
    _probe2 = gf.Component()
    _r2 = gf.routing.route_single(
        _probe2,
        port1=via_rev.ports["o1"],
        port2=combiner.ports["o1"],
        cross_section=cross_section,
    )
    natural_length2 = _r2.length
    extra2 = max(target_length - natural_length2, 0.0)
    final_route2 = gf.routing.route_single(
        c,
        port1=via_rev.ports["o1"],
        port2=combiner.ports["o1"],
        cross_section=cross_section,
        start_straight_length=extra2 / 2,
        end_straight_length=extra2 / 2,
    )
    print(f"[via_MZI] via_rev.o1 → combiner.o1 route length: {final_route2.length:.3f} µm")

    #----- Ports----------------------
    term = c.add_ref(gf.components.terminator(doping_layers=[]))
    term.connect('o1', combiner.ports['o3'])

    c.add_port('o1', port = splitter.ports['o1'])
    c.add_port('o2', port = combiner.ports['o4'])
    return c
