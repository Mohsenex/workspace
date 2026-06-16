import gdsfactory as gf
from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_Si2X2MMI_Cband_v5p0,
    AMF_300LSOI_LSiN2SOISSC_Cband_v5p0,
)
import amf.chp as pdk
from amf.chp.tech import LAYER, TECH

from amf.chp.cells.tapers import taper_strip_to_ridge


@gf.cell
def Rib_MZI(
    gap: float = 180,
    dl: float = 52.004,
    cross_section: str = "strip",
    taper_length: float = 30,
    strip_width: float = 0.55,
) -> gf.Component:
     
    c = gf.Component()
    xs = gf.get_cross_section(cross_section)
    R = xs.radius

    # Defining the cross section for 1.25 um SiN:
    xs_rib_custom = gf.cross_section.rib(
    width=strip_width,
    radius=20,
    radius_min=20,
    layer=LAYER.SLAB,
    cladding_layers=("WG", "SLAB"),
    cladding_offsets=(0, 3),
    cladding_simplify=(50e-3, 50e-3),   # ← add this (50 nm in µm units)
    )
     
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
    # Strip to Rib Placement
    #-------------------------------------------------------
    strip2rib_up1 = c.add_ref(taper_strip_to_ridge(
    length=taper_length,
    width1=0.5,   # strip width
    width2=strip_width,   # rib core width
    w_slab2=6.5,  # matches AMF rib slab width
    ))
    strip2rib_up1.move([55 + 2*R, 2*R + 0.9])
    
    strip2rib_up2 = c.add_ref(taper_strip_to_ridge(
    length=taper_length,
    width1=0.5,   # strip width
    width2=strip_width,   # rib core width
    w_slab2=6.5,  # matches AMF rib slab width
    ))
    strip2rib_up2.mirror_x()
    strip2rib_up2.move([55 + 2*R + 2*taper_length, 2*R + 0.9])

    # Bottom Arm
    strip2rib_bottom1 = c.add_ref(taper_strip_to_ridge(
    length=taper_length,
    width1=0.5,   # strip width
    width2=strip_width,   # rib core width
    w_slab2=6.5,  # matches AMF rib slab width
    ))
    strip2rib_bottom1.move([55 + 2*R, -(2*R + 0.9) - dl/2])
    
    strip2rib_bottom2 = c.add_ref(taper_strip_to_ridge(
    length=taper_length,
    width1=0.5,   # strip width
    width2=strip_width,   # rib core width
    w_slab2=6.5,  # matches AMF rib slab width
    ))
    strip2rib_bottom2.mirror_x()
    strip2rib_bottom2.move([55 + 2*R + dl + 2*taper_length, -(2*R + 0.9) - dl/2])


    #---------------------------------------------------------------------
    # Routing
    #---------------------------------------------------------------------
    # Upper arm:
    r1 = gf.routing.route_single(
        c,
        port1=splitter.ports["o2"],
        port2=strip2rib_up1.ports["o1"],
        cross_section='strip',
    )
    r2 = gf.routing.route_single(
        c,
        port1=strip2rib_up2.ports["o1"],
        port2=combiner.ports["o2"],
        cross_section=cross_section,
    )

    # Routing for the lower arm:
    r3 = gf.routing.route_single(
        c,
        port1=splitter.ports["o3"],
        port2=strip2rib_bottom1.ports["o1"],
        cross_section=cross_section,
    )
    r4 = gf.routing.route_single(
        c,
        port1=strip2rib_bottom2.ports["o1"],
        port2=combiner.ports["o1"],
        cross_section=cross_section,
    )

    # Rib section:
    r5 = gf.routing.route_single(
        c,
        port1=strip2rib_bottom1.ports["o2"],
        port2=strip2rib_bottom2.ports["o2"],
        cross_section=xs_rib_custom,
    )

    #----- Ports----------------------
    term = c.add_ref(gf.components.terminator(doping_layers=[]))
    term.connect('o1', combiner.ports['o3'])

    c.add_port('o1', port = splitter.ports['o1'])
    c.add_port('o2', port = combiner.ports['o4'])
    return c
