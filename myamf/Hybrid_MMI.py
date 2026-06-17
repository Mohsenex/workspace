import gdsfactory as gf
from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_Si2X2MMI_Cband_v5p0,
)

@gf.cell
def Hybrid_MMI()->gf.Component:
    # c = gf.Component()
    # mmi12 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    # mmi221 = c.add_ref(AMF_300LSOI_Si2X2MMI_Cband_v5p0())
    # mmi221.movex(95)
    # mmi222 = c.add_ref(AMF_300LSOI_Si2X2MMI_Cband_v5p0())
    # mmi222.rotate(90)
    # mmi222.move([75, 20])
    # mmi223 = c.add_ref(AMF_300LSOI_Si2X2MMI_Cband_v5p0())
    # mmi223.rotate(-90)
    # mmi223.move([75, -20])

    # gf.routing.route_single(
    #     c,
    #     port1=mmi12.ports["o2"],
    #     port2=mmi222.ports["o2"],
    #     cross_section='strip',        
    #     )
    # gf.routing.route_single(
    #     c,
    #     port1=mmi12.ports["o3"],
    #     port2=mmi223.ports["o1"],
    #     cross_section='strip',        
    #     )
    # gf.routing.route_single(
    #     c,
    #     port1=mmi222.ports["o1"],
    #     port2=mmi221.ports["o2"],
    #     cross_section='strip',        
    #     )
    # gf.routing.route_single(
    #     c,
    #     port1=mmi223.ports["o2"],
    #     port2=mmi221.ports["o1"],
    #     cross_section='strip',        
    #     )

    c = gf.Component()
    mmi12 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    mmi221 = c.add_ref(AMF_300LSOI_Si2X2MMI_Cband_v5p0())
    mmi221.movex(80)
    mmi222 = c.add_ref(AMF_300LSOI_Si2X2MMI_Cband_v5p0())
    # mmi222.rotate(90)
    mmi222.move([80, 25])
    mmi223 = c.add_ref(AMF_300LSOI_Si2X2MMI_Cband_v5p0())
    # mmi223.rotate(-90)
    mmi223.move([80, -25])

    gf.routing.route_single(
        c,
        port1=mmi12.ports["o2"],
        port2=mmi222.ports["o2"],
        cross_section='strip',        
        )
    gf.routing.route_single(
        c,
        port1=mmi12.ports["o3"],
        port2=mmi223.ports["o1"],
        cross_section='strip',        
        )
    gf.routing.route_single(
        c,
        port1=mmi222.ports["o1"],
        port2=mmi221.ports["o2"],
        cross_section='strip',        
        )
    gf.routing.route_single(
        c,
        port1=mmi223.ports["o2"],
        port2=mmi221.ports["o1"],
        cross_section='strip',        
        )

    term = c.add_ref(gf.components.terminator(doping_layers=[]))
    term.connect('o1', mmi221.ports['o4'])

    c.add_port("o1", port=mmi12.ports["o1"]) 
    c.add_port("o2", port=mmi221.ports["o3"])
    c.add_port("o3", port=mmi221.ports["o4"]) 
    c.add_port("o4", port=mmi222.ports["o3"])
    c.add_port("o5", port=mmi222.ports["o4"])
    c.add_port("o6", port=mmi223.ports["o3"])
    c.add_port("o7", port=mmi223.ports["o4"])

    return c
