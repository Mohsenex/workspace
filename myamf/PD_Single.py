import gdsfactory as gf
from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_LSiN2SOISSC_Cband_v5p0,
    AMF_300LSOI_PowMonitor_Cband_Cell_v5p0)
from amf.chp.tech import LAYER
from gdsfactory.pdk import get_active_pdk


@gf.cell
def _PD_Single_core() -> gf.Component:
    """Proven top-oriented single PD (pads on top, PD below, optics down). Unchanged."""
    c = gf.Component()
    pdk = get_active_pdk()

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

    pd1 = c.add_ref(AMF_300LSOI_PowMonitor_Cband_Cell_v5p0())
    pd1.rotate(90)
    pd1.xmin = pads[0].ports['e3'].center[0]
    pd1.ymax = pads[0].ports['e4'].center[1] - 80

    def stack(contact, pad):
        mt1 = c.add_ref(gf.components.compass(size=(10, 12), layer=LAYER.MT1))
        mt1.xmin = contact.center[0] - 5
        mt1.ymin = contact.center[1]
        via2 = c.add_ref(gf.components.compass(size=(5, 5), layer=LAYER.VIA2)); via2.move(mt1.center)
        mt2  = c.add_ref(gf.components.compass(size=(10, 10), layer=LAYER.MT2)); mt2.move(mt1.center)
        gf.routing.route_single(c, port1=mt2.ports['e2'], port2=pad.ports['e4'], cross_section='metal_routing')

    stack(pd1.ports['e1'], pads[0])
    stack(pd1.ports['e2'], pads[1])

    c.add_port('o1', port=pd1.ports['o1'])
    return c


@gf.cell
def PD_Single(bottom: bool = False) -> gf.Component:
    """bottom=True rotates the proven core 180 deg as a rigid unit (pads down, optics up).
    PowMonitor net transform = rotate(270): pure rotation, no mirror. Replaces
    PD_Single() + .mirror_y()."""
    c = gf.Component()
    ref = c.add_ref(_PD_Single_core())
    if bottom:
        ref.rotate(180)
    c.add_ports(ref.ports)
    return c
