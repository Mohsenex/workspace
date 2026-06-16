import gdsfactory as gf
from .Hybrid_MMI import Hybrid_MMI
from .Balanced_PD import Balanced_PD

@gf.cell
def Hybrid_MMI_Balanced_PD()->gf.Component:
    c = gf.Component()
    
    hmmi = c.add_ref(Hybrid_MMI())
    bpd1 = c.add_ref(Balanced_PD())
    bpd1.move((-120, 220))
    bpd2 = c.add_ref(Balanced_PD())
    bpd2.xmin = bpd1.xmax + 35
    bpd2.ymin = bpd1.ymin

    gf.routing.route_bundle(
        c,
        ports1 = [hmmi.ports['o4'], hmmi.ports['o5']],
        ports2 = [bpd1.ports['o1'], bpd1.ports['o2']],
        cross_section = 'strip'
    )

    gf.routing.route_single(
        c,
        port1 = hmmi.ports['o6'],
        port2 = bpd2.ports['o1'],
        cross_section = 'strip',
        waypoints = [
            (hmmi.ports['o6'].center[0] + 40, hmmi.ports['o6'].center[1]),
            (hmmi.ports['o6'].center[0] + 40, hmmi.ports['o6'].center[1]+20),
            (bpd2.ports['o1'].center[0], hmmi.ports['o6'].center[1]+20),
        ],
    )

    gf.routing.route_single(
        c,
        port1 = hmmi.ports['o7'],
        port2 = bpd2.ports['o2'],
        cross_section = 'strip',
    )

    c.add_port('o1', port = hmmi.ports['o1'])
    c.add_port('o2', port = hmmi.ports['o2'])
    c.add_port('o3', port = hmmi.ports['o3'])
    return c
