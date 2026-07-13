import gdsfactory as gf
from gdsfactory.pdk import get_active_pdk
from amf.chp.cells.fixed import AMF_300LSOI_PowMonitor_Cband_Cell_v5p0
from amf.chp.tech import LAYER, TECH


@gf.cell
def _Balanced_PD_core(pad_dy: float = 0) -> gf.Component:
    """The proven top-oriented balanced PD (pads on top, PDs below, optics down).
    This is the EXACT working layout — do not change it. The bottom variant is built
    by rigidly rotating this whole cell 180 deg in Balanced_PD(), which keeps every
    MT1/VIA2/MT2 stamp and route correct by construction.
    """
    c = gf.Component()
    pdk = get_active_pdk()
    pitch = 125

    pad1 = c.add_ref(pdk.get_component("pad")); pad1.movey(pad_dy)
    pad2 = c.add_ref(pdk.get_component("pad")); pad2.move((1 * pitch, pad_dy))
    pad3 = c.add_ref(pdk.get_component("pad")); pad3.move((2 * pitch, pad_dy))

    pd1 = c.add_ref(AMF_300LSOI_PowMonitor_Cband_Cell_v5p0()); pd1.rotate(90); pd1.move((100, -150))
    pd2 = c.add_ref(AMF_300LSOI_PowMonitor_Cband_Cell_v5p0()); pd2.rotate(90); pd2.move((150, -150))

    def stack(contact, pad, w=(10, 12)):
        mt1 = c.add_ref(gf.components.compass(size=w, layer=LAYER.MT1))
        mt1.xmin = contact.center[0] - 5
        mt1.ymin = contact.center[1]
        via2 = c.add_ref(gf.components.compass(size=(5, 5), layer=LAYER.VIA2)); via2.move(mt1.center)
        mt2  = c.add_ref(gf.components.compass(size=(10, 10), layer=LAYER.MT2)); mt2.move(mt1.center)
        gf.routing.route_single(c, port1=mt2.ports['e2'], port2=pad.ports['e4'], cross_section="metal_routing")

    stack(pd1.ports['e1'], pad1)                  # left  -> pad1
    stack(pd2.ports['e2'], pad3)                  # right -> pad3
    stack(pd1.ports['e2'], pad2, w=(29.7, 12))    # middle (common P/N node) -> pad2

    c.add_port("o1", port=pd1.ports["o1"])
    c.add_port("o2", port=pd2.ports["o1"])
    return c


@gf.cell
def Balanced_PD(pad_dy: float = 0, bottom: bool = False) -> gf.Component:
    """bottom=False : original top layout (pads up, optics down).
    bottom=True  : the SAME layout rotated 180 deg as one rigid unit (pads down, optics up).
                   PowMonitor BB net transform = rotate(90)+rotate(180) = rotate(270): a pure
                   rotation, never mirrored -> AMF-compliant, and all wiring stays intact.
                   Replaces the old Balanced_PD(...) + .mirror_y() at the call sites.
    """
    c = gf.Component()
    ref = c.add_ref(_Balanced_PD_core(pad_dy=pad_dy))
    if bottom:
        ref.rotate(180)
    c.add_ports(ref.ports)
    return c
