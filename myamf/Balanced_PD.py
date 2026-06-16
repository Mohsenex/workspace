import gdsfactory as gf
from gdsfactory.pdk import get_active_pdk
from amf.chp.cells.fixed import AMF_300LSOI_PowMonitor_Cband_Cell_v5p0
from amf.chp.tech import LAYER, TECH

@gf.cell
def Balanced_PD()->gf.Component:
    c = gf.Component()
    
    # PAD_PITCH = 125.0
    # pad_cell = pdk.get_component("pad")

    # pads = []
    # x_start = die.x - (N_PADS - 1) * PAD_PITCH / 2
    # for i in range(3):
    #     p = c.add_ref(pad_cell)
    #     p.x = x_start + i * PAD_PITCH
    #     p.ymax = die.ymax - 50
    #     pads.append(p)
    pdk = get_active_pdk()
    pitch = 125
    pad1 = c.add_ref(pdk.get_component("pad"))
    pad2 = c.add_ref(pdk.get_component("pad"))
    pad2.move((1*pitch, 0))
    pad3 = c.add_ref(pdk.get_component("pad"))
    pad3.move((2*pitch, 0))

    pd1 = c.add_ref(AMF_300LSOI_PowMonitor_Cband_Cell_v5p0())
    pd1.rotate(90)
    pd1.move((100, -150))
    pd2 = c.add_ref(AMF_300LSOI_PowMonitor_Cband_Cell_v5p0())
    pd2.rotate(90)
    pd2.move((150, -150))


    #------- Connecting the left port of pd1 to pad1
    mt1_1 = c.add_ref(gf.components.compass(size = (10, 10), layer = LAYER.MT1))
    mt1_1.xmin = pd1.ports['e1'].center[0]-5
    mt1_1.ymin = pd1.ports['e1'].center[1]

    via2_1 = c.add_ref(gf.components.compass(size = (5, 5), layer = LAYER.VIA2))
    via2_1.move(mt1_1.center)

    mt2_1 = c.add_ref(gf.components.compass(size = (10, 10), layer = LAYER.MT2))
    mt2_1.move(mt1_1.center)

    # MT2 segment: via stack → pad (both on MT2)
    gf.routing.route_single(
        c,
        port1=mt2_1.ports['e2'],
        port2=pad1.ports['e4'],
        cross_section="metal_routing",
    )
    #------- Connecting the right port of pd2 to pad3
    mt1_3 = c.add_ref(gf.components.compass(size = (10, 10), layer = LAYER.MT1))
    mt1_3.xmin = pd2.ports['e2'].center[0]-5
    mt1_3.ymin = pd2.ports['e2'].center[1]

    via2_3 = c.add_ref(gf.components.compass(size = (5, 5), layer = LAYER.VIA2))
    via2_3.move(mt1_3.center)

    mt2_3 = c.add_ref(gf.components.compass(size = (10, 10), layer = LAYER.MT2))
    mt2_3.move(mt1_3.center)

    # MT2 segment: via stack → pad (both on MT2)
    gf.routing.route_single(
        c,
        port1=mt2_3.ports['e2'],
        port2=pad3.ports['e4'],
        cross_section="metal_routing",
    )

    #------- Connecting the middle ports to pad2
    mt1_2 = c.add_ref(gf.components.compass(size = (29.7, 10), layer = LAYER.MT1))
    mt1_2.xmin = pd1.ports['e2'].center[0]-5
    mt1_2.ymin = pd1.ports['e2'].center[1]

    via2_2 = c.add_ref(gf.components.compass(size = (5, 5), layer = LAYER.VIA2))
    via2_2.move(mt1_2.center)

    mt2_2 = c.add_ref(gf.components.compass(size = (10, 10), layer = LAYER.MT2))
    mt2_2.move(mt1_2.center)

    # MT2 segment: via stack → pad (both on MT2)
    gf.routing.route_single(
        c,
        port1=mt2_2.ports['e2'],
        port2=pad2.ports['e4'],
        cross_section="metal_routing",
    )

    #--------- Adding Ports -------------------------------
    c.add_port("o1", port=pd1.ports["o1"])  
    c.add_port("o2", port=pd2.ports["o1"])  

    return c
