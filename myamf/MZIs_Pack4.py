import gdsfactory as gf
from amf.import_gds import import_gds
from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_LSiN2SOISSC_Cband_v5p0,
    AMF_300LSOI_PowMonitor_Cband_Cell_v5p0)
from .SiN_MZI import SiN_MZI
from .via_MZI import via_MZI

@gf.cell
def MZIs_Pack4()->gf.Component:
    c = gf.Component()
    
    mzi = gf.import_gds("/workspace/myamf/gds/NeffMZIGrattoSlabRibtoStrip_Alternative_V2.gds")
    mzi.add_port(name="o1", center=(-546.09, 46.044), width=0.5, orientation=180, layer='WG')
    mzi.add_port(name="o2", center=(-546.09, 44.71), width=0.5, orientation=180, layer='WG')
    mzi.add_port(name="o3", center=(463.91, 46.044), width=0.5, orientation=0, layer='WG')
    mzi.add_port(name="o4", center=(463.91, 44.71), width=0.5, orientation=0, layer='WG')

    mzi1 = c.add_ref(mzi)
    mzi2 = c.add_ref(mzi)
    mzi2.xmin = mzi1.xmin + 160
    mzi2.ymax = mzi1.ymin + 125

    via_mzi = c.add_ref(via_MZI())
    via_mzi.xmin = mzi2.xmin - 210
    via_mzi.ymax = mzi2.y - 40
    sin_mzi = c.add_ref(SiN_MZI(gap = 400, dl = 97.055, cross_section = "strip"))
    sin_mzi.xmin = mzi2.xmin - 210
    sin_mzi.ymax = via_mzi.ymin - 60



    via = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via.x = mzi1.xmin + 250
    via.y = via.y + 150

    splitter0 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    splitter0.mirror_x()
    splitter0.connect('o1', via.ports['o1'])

    splitter1 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    splitter1.mirror_x()
    splitter1.xmax = splitter0.xmin - 25
    splitter1.ymin = splitter0.ymin - 25

    splitter2 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    splitter2.mirror_x()
    splitter2.xmax = splitter1.xmin - 25
    splitter2.ymin = splitter1.ymax + 25

    splitter3 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    splitter3.mirror_x()
    splitter3.xmax = splitter1.xmin - 25
    splitter3.ymin = splitter1.ymin - 25

    term1 = c.add_ref(gf.components.terminator(doping_layers=[]))
    term1.connect('o1', mzi1.ports['o2'])
    term2 = c.add_ref(gf.components.terminator(doping_layers=[]))
    term2.connect('o1', mzi1.ports['o3'])
    term3 = c.add_ref(gf.components.terminator(doping_layers=[]))
    term3.connect('o1', mzi2.ports['o2'])
    term4 = c.add_ref(gf.components.terminator(doping_layers=[]))
    term4.connect('o1', mzi2.ports['o3'])

    gf.routing.route_single(
        c,
        port1 = splitter3.ports['o3'],
        port2 = mzi1.ports['o1'],
        cross_section = 'strip',
        waypoints = [
            (term1.xmin - 10, float(splitter3.ports['o3'].center[1])),
            (term1.xmin - 10, float(mzi1.ports['o1'].center[1])),
        ]
    )
    gf.routing.route_single(
        c,
        port1 = splitter3.ports['o2'],
        port2 = mzi2.ports['o1'],
        cross_section = 'strip',
        waypoints = [
            (term1.xmin - 15, float(splitter3.ports['o2'].center[1])),
            (term1.xmin - 15, float(mzi2.ports['o1'].center[1])),
        ]
    )

    gf.routing.route_single(
        c,
        port1 = splitter2.ports['o3'],
        port2 = via_mzi.ports['o1'],
        cross_section = 'strip',
        waypoints = [
            (term1.xmin - 20, float(splitter2.ports['o3'].center[1])),
            (term1.xmin - 20, float(via_mzi.ports['o1'].center[1])),
        ]
    )
    gf.routing.route_single(
        c,
        port1 = splitter2.ports['o2'],
        port2 = sin_mzi.ports['o1'],
        cross_section = 'strip',
        waypoints = [
            (term1.xmin - 25, float(splitter2.ports['o2'].center[1])),
            (term1.xmin - 25, float(sin_mzi.ports['o1'].center[1])),
        ]
    )

    gf.routing.route_bundle(
        c,
        ports1 = [splitter1.ports['o2'], splitter1.ports['o3']],
        ports2 = [splitter2.ports['o1'], splitter3.ports['o1']],
        cross_section = 'strip',
    )

    gf.routing.route_single(
        c,
        port1 = splitter0.ports['o3'],
        port2 = splitter1.ports['o1'],
        cross_section = 'strip',
    )


    #--------- second via ------------------
    via2 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via2.mirror_x()
    via2.x = mzi1.xmin + 20
    via2.y = via.y + 30

    gf.routing.route_single(
        c,
        port1 = splitter0.ports['o2'],
        port2 = via2.ports['o1'],
        cross_section = 'strip',
    )


    c.add_port('o1', port = via.ports['o2'])
    c.add_port('o2', port = mzi1.ports['o4'])
    c.add_port('o3', port = mzi2.ports['o4'])
    c.add_port('o4', port = via_mzi.ports['o2'])
    c.add_port('o5', port = sin_mzi.ports['o2'])
    c.add_port('o6', port = via2.ports['o2'])
    return c
