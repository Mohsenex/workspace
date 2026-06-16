import gdsfactory as gf
from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_Si2X2MMI_Cband_v5p0,
    AMF_300LSOI_LSiN2SOISSC_Cband_v5p0,
)
import amf.chp as pdk
from amf.chp.tech import LAYER


@gf.cell
def SiN_1250_MZI(
    gap: float = 400,
    dl: float = 17.179,
    cross_section: str = "strip",
    taper_length: float = 50,
    taper_width: float = 1.25,
) -> gf.Component:
     
    c = gf.Component()
    xs = gf.get_cross_section(cross_section)
    R = xs.radius

    # Defining the cross section for 1.25 um SiN:
    xs_sin_1250 = gf.cross_section.strip(
    width=1.25,
    radius=25,
    radius_min=25,
    layer=LAYER.WG_SIN,
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
    # Via and taper Placement
    #-------------------------------------------------------
    via_up1 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via_up1.move([55 + 2*R, 2*R + 0.9])

    taper_up1 = c.add_ref(gf.components.taper(
        length=taper_length,        # taper length in µm (adjust as needed)
        width1=1.0,         # 1000 nm → 1.0 µm
        width2=taper_width,        # 1250 nm → 1.25 µm
        cross_section="nitride",
    ))
    taper_up1.move([55 + 2*R + 121, 2*R + 0.9])

    taper_up2 = c.add_ref(gf.components.taper(
        length=taper_length,        # taper length in µm (adjust as needed)
        width1=1.0,         # 1000 nm → 1.0 µm
        width2=taper_width,        # 1250 nm → 1.25 µm
        cross_section="nitride",
    ))
    taper_up2.mirror_x()
    taper_up2.move([55 + 2*R + 121 + 2*taper_length, 2*R + 0.9])
    


    via_up2 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via_up2.mirror_x()
    via_up2.move([242 + 55 + 2*R + 2*taper_length, 2*R + 0.9])


    via_bottom1 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via_bottom1.move([55 + 2*R, - (2*R + 0.9) - dl/2])
    
    taper_bottom1 = c.add_ref(gf.components.taper(
        length=taper_length,        # taper length in µm (adjust as needed)
        width1=1.0,         # 1000 nm → 1.0 µm
        width2=taper_width,        # 1250 nm → 1.25 µm
        cross_section="nitride",
    ))
    taper_bottom1.move([55 + 2*R + 121, -(2*R + 0.9) - dl/2])

    taper_bottom2 = c.add_ref(gf.components.taper(
        length=taper_length,        # taper length in µm (adjust as needed)
        width1=1.0,         # 1000 nm → 1.0 µm
        width2=taper_width,        # 1250 nm → 1.25 µm
        cross_section="nitride",
    ))
    taper_bottom2.mirror_x()
    taper_bottom2.move([55 + 2*R + 121 + dl + 2*taper_length, -(2*R + 0.9) - dl/2])

    via_bottom2 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via_bottom2.mirror_x()
    via_bottom2.move([242 + 55 + 2*R + dl + 2*taper_length, -(2*R + 0.9) - dl/2])

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
        port1=taper_bottom1.ports["o2"],
        port2=taper_bottom2.ports["o2"],
        cross_section=xs_sin_1250,
    )

    #----- Ports----------------------
    term = c.add_ref(gf.components.terminator(doping_layers=[]))
    term.connect('o1', combiner.ports['o3'])

    c.add_port('o1', port = splitter.ports['o1'])
    c.add_port('o2', port = combiner.ports['o4'])
    return c
