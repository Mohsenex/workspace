import gdsfactory as gf
from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_LSiN2SOISSC_Cband_v5p0,
    AMF_300LSOI_PowMonitor_Cband_Cell_v5p0)
from amf.chp.tech import LAYER
from gdsfactory.pdk import get_active_pdk


@gf.cell
def PD_Single() -> gf.Component:
    c = gf.Component()
    pdk = get_active_pdk()

    #---------------------------------------------------------------------------------------
    # PADs — 2 pads, 125 µm pitch
    #---------------------------------------------------------------------------------------
    N_PADS = 2
    PAD_PITCH = 125.0
    pad_cell = pdk.get_component("pad")

    pads = []
    x_start = 0
    for i in range(N_PADS):
        p = c.add_ref(pad_cell)
        p.x = x_start + i * PAD_PITCH
        p.ymax = 0
        pads.append(p)

    #---------------------------------------------------------------------------------------
    # PD
    #---------------------------------------------------------------------------------------
    pd1 = c.add_ref(AMF_300LSOI_PowMonitor_Cband_Cell_v5p0())
    pd1.rotate(90)
    pd1.xmin = pads[0].ports['e3'].center[0]
    pd1.ymax = pads[0].ports['e4'].center[1] - 80

    #---------------------------------------------------------------------------------------
    # Contacts: M1/VIA2/M2 stack stamped directly on each PD contact, then MT2 to the pad.
    # Same pattern as Balanced_PD -> the only route is MT2->MT2 (no MT1 routing, no taper).
    #---------------------------------------------------------------------------------------
    # ---- contact e1 -> pads[0]
    mt1_e1 = c.add_ref(gf.components.compass(size=(10, 12), layer=LAYER.MT1))
    mt1_e1.xmin = pd1.ports['e1'].center[0] - 5
    mt1_e1.ymin = pd1.ports['e1'].center[1]

    via2_e1 = c.add_ref(gf.components.compass(size=(5, 5), layer=LAYER.VIA2))
    via2_e1.move(mt1_e1.center)

    mt2_e1 = c.add_ref(gf.components.compass(size=(10, 10), layer=LAYER.MT2))
    mt2_e1.move(mt1_e1.center)

    gf.routing.route_single(
        c,
        port1=mt2_e1.ports['e2'],
        port2=pads[0].ports['e4'],
        cross_section='metal_routing',
    )

    # ---- contact e2 -> pads[1]
    mt1_e2 = c.add_ref(gf.components.compass(size=(10, 12), layer=LAYER.MT1))
    mt1_e2.xmin = pd1.ports['e2'].center[0] - 5
    mt1_e2.ymin = pd1.ports['e2'].center[1]

    via2_e2 = c.add_ref(gf.components.compass(size=(5, 5), layer=LAYER.VIA2))
    via2_e2.move(mt1_e2.center)

    mt2_e2 = c.add_ref(gf.components.compass(size=(10, 10), layer=LAYER.MT2))
    mt2_e2.move(mt1_e2.center)

    gf.routing.route_single(
        c,
        port1=mt2_e2.ports['e2'],
        port2=pads[1].ports['e4'],
        cross_section='metal_routing',
    )

    #--------- Adding Ports -------------------------------
    c.add_port('o1', port=pd1.ports['o1'])
    return c
