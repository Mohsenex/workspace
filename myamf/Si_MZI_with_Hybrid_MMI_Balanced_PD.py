import gdsfactory as gf
from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,)
from .Hybrid_MMI_Balanced_PD import Hybrid_MMI_Balanced_PD

@gf.cell
def Si_MZI_with_Hybrid_MMI_Balanced_PD(
    dl: float = 21,
)->gf.Component:
    c = gf.Component()
    
    hmmi = c.add_ref(Hybrid_MMI_Balanced_PD())
    splitter = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    splitter.move((-100 -55, 0))

    arm_top = gf.routing.route_single(
        c,
        port1 = hmmi.ports['o2'],
        port2 = splitter.ports['o2'],
        cross_section = 'strip',
        waypoints=[
            (hmmi.ports['o2'].center[0] + 20, hmmi.ports['o2'].center[1]),
            (hmmi.ports['o2'].center[0] + 20, hmmi.ports['o2'].center[1] + 145),
            (splitter.ports['o2'].center[0] + 15, hmmi.ports['o2'].center[1] + 145),
            (splitter.ports['o2'].center[0] + 15, splitter.ports['o2'].center[1]),
        ]
    )

    arm_bottom = gf.routing.route_single(
        c,
        port1 = splitter.ports['o3'],
        port2 = hmmi.ports['o1'],
        cross_section = 'strip',
        waypoints=[
            (splitter.ports['o3'].center[0]+10, splitter.ports['o3'].center[1]),
            (splitter.ports['o3'].center[0]+10, splitter.ports['o3'].center[1]-55),
            (hmmi.ports['o1'].center[0]+180.29625 + dl/2, splitter.ports['o3'].center[1]-55),
            (hmmi.ports['o1'].center[0]+180.29625 + dl/2, splitter.ports['o3'].center[1]-35),
            (hmmi.ports['o1'].center[0]-10, splitter.ports['o3'].center[1]-35),
            (hmmi.ports['o1'].center[0]-10, hmmi.ports['o1'].center[1]),
        ],
    )

    c.add_port('o1', port = splitter.ports['o1'])

    # rect =c.add_ref(gf.components.rectangle(size= (arm_top.length/1000, 10)))
    # rect.move((0,300))
    # rect2 =c.add_ref(gf.components.rectangle(size= (arm_bottom.length/1000, 10)))
    # rect2.move((0,295))
    

    return c
