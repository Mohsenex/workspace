import gdsfactory as gf
from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_LSiN2SOISSC_Cband_v5p0)
from .Hybrid_MMI_Balanced_PD import Hybrid_MMI_Balanced_PD

@gf.cell
def SiN_MZI_with_Hybrid_MMI_Balanced_PD(
    dl: float = 450,
)->gf.Component:
    c = gf.Component()
    
    hmmi = c.add_ref(Hybrid_MMI_Balanced_PD())
    splitter = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    splitter.move((-100 -55, 0))
    
    via_top1 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via_top1.move((-70, 38))
    via_top2 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via_top2.mirror_x()
    via_top2.move((70+242, 38))

    via_bottom1 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via_bottom1.move((16.167, -95))
    via_bottom2 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    # via_bottom2.mirror_x()
    via_bottom2.move((16.167, -35))

    arm_top1 = gf.routing.route_single(
        c,
        port1 = splitter.ports['o2'],
        port2 = via_top1.ports['o1'],
        cross_section = 'strip',
    )
    
    arm_top2 = gf.routing.route_single(
        c,
        port1 = hmmi.ports['o2'],
        port2 = via_top2.ports['o1'],
        cross_section = 'strip',
    )

    arm_top_SiN = gf.routing.route_single(
        c,
        port1 = via_top1.ports['o2'],
        port2 = via_top2.ports['o2'],
        cross_section = 'nitride',
    )

    arm_bottom1 = gf.routing.route_single(
        c,
        port1 = splitter.ports['o3'],
        port2 = via_bottom1.ports['o1'],
        cross_section = 'strip',
    )

    arm_bottom2 = gf.routing.route_single(
        c,
        port1 = via_bottom2.ports['o1'],
        port2 = hmmi.ports['o1'],
        cross_section = 'strip',
    )

    arm_bottom_SiN = gf.routing.route_single(
        c,
        port1 = via_bottom1.ports['o2'],
        port2 = via_bottom2.ports['o2'],
        cross_section = 'nitride',
        waypoints = [
            (via_bottom1.ports['o2'].center[0] + 48.407 + dl/2 , via_bottom1.ports['o2'].center[1]),
            (via_bottom1.ports['o2'].center[0] + 48.407 + dl/2 , via_bottom2.ports['o2'].center[1]),
        ],
    )

    c.add_port('o1', port = splitter.ports['o1'])

    #-------- this is just to visualize the lengths of both arms
    # rect =c.add_ref(gf.components.rectangle(size= ((arm_top1.length + arm_top2.length)/1000, 10)))
    # rect.move((0,300))
    # rect2 =c.add_ref(gf.components.rectangle(size= ((arm_bottom1.length + arm_bottom2.length) /1000, 10)))
    # rect2.move((0,295))
    
    # rect_SiN =c.add_ref(gf.components.rectangle(size= ((arm_top_SiN.length)/1000, 10)))
    # rect_SiN.move((0,320))
    # rect2_SiN =c.add_ref(gf.components.rectangle(size= ((arm_bottom_SiN.length) /1000, 10)))
    # rect2_SiN.move((0,315))

    return c
