import gdsfactory as gf
from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_Si2X2MMI_Cband_v5p0,
    AMF_300LSOI_LSiN2SOISSC_Cband_v5p0,
)
import amf.chp as pdk
from amf.chp.tech import LAYER, TECH

from amf.chp.cells.tapers import taper


@gf.cell
def Athermal_MZI(
    gap: float = 225,
    dl: float = 6.667,
    l = 121.689,
    cross_section: str = "strip",
    taper_length: float = 30,
    strip_width: float = 1,
) -> gf.Component:
     
    c = gf.Component()
    xs = gf.get_cross_section(cross_section)
    R = xs.radius

    # Defining the cross section for Thick section:
    # Strip waveguide with 1000 nm (1.0 µm) width
    xs_custom = gf.cross_section.strip(
        width=strip_width,
        radius=20,
        radius_min=20,
        layer=LAYER.WG,
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
    taper_up1 = c.add_ref(taper(
    length=taper_length,
    width1=0.5,   # strip width
    width2=strip_width,   # rib core width
    ))
    taper_up1.move([55 + 2*R, 2*R + 0.9])
    
    taper_up2 = c.add_ref(taper(
    length=taper_length,
    width1=0.5,   # strip width
    width2=strip_width,   # rib core width
    ))
    taper_up2.mirror_x()
    taper_up2.move([55 + 2*R + 2*taper_length, 2*R + 0.9])

    # Bottom Arm
    taper_bottom1 = c.add_ref(taper(
    length=taper_length,
    width1=0.5,   # strip width
    width2=strip_width,   # rib core width
    ))
    taper_bottom1.move([55 + 2*R, -(2*R + 0.9) - dl/2])
    
    taper_bottom2 = c.add_ref(taper(
    length=taper_length,
    width1=0.5,   # strip width
    width2=strip_width,   # rib core width
    ))
    taper_bottom2.mirror_x()
    taper_bottom2.move([55 + 2*R + l + 2*taper_length, -(2*R + 0.9) - dl/2])


    #---------------------------------------------------------------------
    # Routing
    #---------------------------------------------------------------------
    # Upper arm:
    r1 = gf.routing.route_single(
        c,
        port1=splitter.ports["o2"],
        port2=taper_up1.ports["o1"],
        cross_section='strip',
    )
    r2 = gf.routing.route_single(
        c,
        port1=taper_up2.ports["o1"],
        port2=combiner.ports["o2"],
        cross_section=cross_section,
    )

    # Routing for the lower arm:
    r3 = gf.routing.route_single(
        c,
        port1=splitter.ports["o3"],
        port2=taper_bottom1.ports["o1"],
        cross_section=cross_section,
    )
    r4 = gf.routing.route_single(
        c,
        port1=taper_bottom2.ports["o1"],
        port2=combiner.ports["o1"],
        cross_section=cross_section,
    )

    # thick section:
    r5 = gf.routing.route_single(
        c,
        port1=taper_bottom1.ports["o2"],
        port2=taper_bottom2.ports["o2"],
        cross_section=xs_custom,
    )

    return c
