import gdsfactory as gf
from .Si_MZI_with_Hybrid_MMI_Balanced_PD import Si_MZI_with_Hybrid_MMI_Balanced_PD
from .SiN_MZI_with_Hybrid_MMI_Balanced_PD import SiN_MZI_with_Hybrid_MMI_Balanced_PD
from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_Si2X2MMI_Cband_v5p0,)

@gf.cell
def Wavemeter(
    dl1: float = 6,
    dl2: float = 52,
    dl3: float = 445,
    dl4: float = 445, # SiN MZI
)->gf.Component:
    c = gf.Component()
    mzi1 = c.add_ref(Si_MZI_with_Hybrid_MMI_Balanced_PD(dl = dl1))
    mzi2 = c.add_ref(Si_MZI_with_Hybrid_MMI_Balanced_PD(dl = dl2))
    mzi2.xmin = mzi1.xmax + 35
    mzi3 = c.add_ref(Si_MZI_with_Hybrid_MMI_Balanced_PD(dl = dl3))
    mzi3.xmin = mzi2.xmax + 35
    # SiN MZI:
    mzi4 = c.add_ref(SiN_MZI_with_Hybrid_MMI_Balanced_PD(dl = dl4))
    mzi4.xmin = mzi3.xmax + 35

    mmi1 = c.add_ref(AMF_300LSOI_Si2X2MMI_Cband_v5p0())
    # mmi1.rotate(90)
    mmi1.move((-190, 30))
    mmi2 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    mmi2.rotate(90)
    mmi2.move((-160, 75))
    mmi3 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    mmi3.rotate(90)
    mmi3.move((-140, 75))

    mmi4 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    mmi4.rotate(90)
    mmi4.xmin = mmi1.xmin + 15
    mmi4.ymax = mmi1.ymin - 50

    #----------- Routing---------------------
    gf.routing.route_bundle(
        c,
        ports1 = [mmi1.ports['o3'], mmi1.ports['o4']],
        ports2 = [mmi2.ports['o1'], mmi3.ports['o1']],
        cross_section = 'strip',
    )

    gf.routing.route_single(
        c,
        port1 = mmi3.ports['o3'],
        port2 = mzi1.ports['o1'],
        cross_section = 'strip',
        waypoints =[
            (mmi3.ports['o3'].center[0], mmi3.ports['o3'].center[1] + 10),
            (mmi3.ports['o3'].center[0] + 45, mmi3.ports['o3'].center[1] + 10),
            (mmi3.ports['o3'].center[0] + 45, mzi1.ports['o1'].center[1] + 20),
            (mzi1.ports['o1'].center[0] -10, mzi1.ports['o1'].center[1] + 20),
            (mzi1.ports['o1'].center[0] -10, mzi1.ports['o1'].center[1]),
        ],
    )

    gf.routing.route_single(
        c,
        port1 = mmi3.ports['o2'],
        port2 = mzi2.ports['o1'],
        cross_section = 'strip',
        waypoints =[
            (mmi3.ports['o2'].center[0], mmi3.ports['o2'].center[1] + 20),
            (mzi2.ports['o1'].center[0] -10, mmi3.ports['o2'].center[1] + 20),
            (mzi2.ports['o1'].center[0] -10, mzi2.ports['o1'].center[1]),
        ],
    )
    
    # The left MMI is mmi2

    gf.routing.route_single(
        c,
        port1 = mmi2.ports['o3'],
        port2 = mzi3.ports['o1'],
        cross_section = 'strip',
        waypoints =[
            (mmi2.ports['o3'].center[0], mmi2.ports['o3'].center[1] + 23),
            (mzi3.ports['o1'].center[0] -10, mmi2.ports['o3'].center[1] + 23),
            (mzi3.ports['o1'].center[0] -10, mzi3.ports['o1'].center[1]),
        ],
    )

    gf.routing.route_single(
        c,
        port1 = mmi2.ports['o2'],
        port2 = mzi4.ports['o1'],
        cross_section = 'strip',
        waypoints =[
            (mmi2.ports['o2'].center[0], mmi2.ports['o2'].center[1] + 26),
            (mzi4.ports['o1'].center[0] -10, mmi2.ports['o2'].center[1] + 26),
            (mzi4.ports['o1'].center[0] -10, mzi4.ports['o1'].center[1]),
        ],
    )

    gf.routing.route_single(
        c,
        port1 = mmi1.ports['o1'],
        port2 = mmi4.ports['o3'],
        cross_section = 'strip',
        
    )
    c.add_port('o1', port = mmi1.ports['o2'])
    c.add_port('o2', port = mmi4.ports['o2'])
    c.add_port('o3', port = mmi4.ports['o1'])

    return c
