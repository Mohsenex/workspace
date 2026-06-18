import gdsfactory as gf
from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_LSiN2SOISSC_Cband_v5p0,
    AMF_300LSOI_PowMonitor_Cband_Cell_v5p0)
from gdsfactory.pdk import get_active_pdk

@gf.cell
def PD_Single()->gf.Component:
    c = gf.Component()

    pdk = get_active_pdk()
    #---------------------------------------------------------------------------------------
    # PADs — 38 individual pads, 125 µm pitch, centered at top of die
    #---------------------------------------------------------------------------------------
    N_PADS = 2
    PAD_PITCH = 125.0
    pad_cell = pdk.get_component("pad")

    pads = []
    x_start = 0  #die.x - (N_PADS - 1) * PAD_PITCH / 2 + 1400
    for i in range(N_PADS):
        p = c.add_ref(pad_cell)
        p.x = x_start + i * PAD_PITCH
        p.ymax = 0
        pads.append(p)

    pd1 = c.add_ref(AMF_300LSOI_PowMonitor_Cband_Cell_v5p0())
    pd1.rotate(90)
    pd1 .xmin = pads[0].ports['e3'].center[0]
    pd1.ymax = pads[0].ports['e4'].center[1] - 80
    via_pd1_e1 = c.add_ref(pdk.get_component("via_stack_m1_m2"))
    via_pd1_e2 = c.add_ref(pdk.get_component("via_stack_m1_m2"))
    via_pd1_e1.x = float(pads[0].ports['e4'].center[0])
    via_pd1_e1.y = float(pd1.ports['e1'].center[1]  + 40)
    via_pd1_e2.x = float(pads[1].ports['e4'].center[0])
    via_pd1_e2.y = float(pd1.ports['e2'].center[1] +40)

    gf.routing.route_bundle(
        c,
        ports1=[pd1.ports['e1'], pd1.ports['e2']],
        ports2=[via_pd1_e1.ports['e3'], via_pd1_e2.ports['e1']],
        cross_section='metal1',
        auto_taper=False,
        allow_layer_mismatch=True,
        allow_width_mismatch=True,
    )
    gf.routing.route_single(
        c,
        port1=via_pd1_e1.ports['e2'],
        port2=pads[0].ports['e4'],
        cross_section='metal_routing',
    )
    gf.routing.route_single(
        c,
        port1=via_pd1_e2.ports['e2'],
        port2=pads[1].ports['e4'],
        cross_section='metal_routing',
    )

    c.add_port('o1', port = pd1.ports['o1'])
    return c
