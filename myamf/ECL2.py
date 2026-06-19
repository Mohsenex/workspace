import gdsfactory as gf
from gdsfactory.pdk import get_active_pdk

from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_LSiN2SOISSC_Cband_v5p0)
from amf.config import PATH
from amf.chp.tech import LAYER, TECH
from amf.import_gds import import_gds

from amf.chp.tech import LAYER, TECH
from .Balanced_PD import Balanced_PD


gdsdir = PATH.gds_chp

N_FIBERS = 22
PITCH = 127.0  # um
DIE_SIZE = (7400, 3000)


@gf.cell
def ECL2() -> gf.Component:
    c = gf.Component()
    pdk = get_active_pdk()

    die = c.add_ref(gf.components.rectangle(size=DIE_SIZE, layer = LAYER.MARKER))
    die.move((-3700, -1500))

    
    #---------------------------------------------------------------------------------------
    # PADs — 38 individual pads, 125 µm pitch, centered at top of die
    #---------------------------------------------------------------------------------------
    N_PADS = 30
    PAD_PITCH = 125.0
    pad_cell = pdk.get_component("pad")

    pads = []
    x_start = die.xmin + 150  #die.x - (N_PADS - 1) * PAD_PITCH / 2 + 1400
    for i in range(N_PADS):
        p = c.add_ref(pad_cell)
        p.x = x_start + i * PAD_PITCH
        p.ymax = die.ymax - 50
        pads.append(p)

    # Access individual pads as: pads[0], pads[1], ..., pads[37]
    # Each pad has ports: e1 (west), e2 (north), e3 (east), e4 (south)

   
    # routing SiN with bending radius of 45 um
    xs_sin = gf.cross_section.strip(
    width= 1,
    radius=45,
    radius_min=45,
    layer=LAYER.WG_SIN,
    )
    #---------------------------------------------------------------------------------------
    # ECL2 
    #---------------------------------------------------------------------------------------

    ecl2 = gf.import_gds("/workspace/myamf/gds/FonexQuietXECL_SiN_V2026_6.gds", skip_new_cells=True)
    # SiN Ports:
    ecl2.add_port(name="o1", center=(-1425.95, -232.72), width=1.0, orientation=180, layer='WG_SIN')
    ecl2.add_port(name="o2", center=(-1425.96, -282.72), width=1.0, orientation=180, layer='WG_SIN')
    ecl2.add_port(name="o3", center=(-886.95,  -432.72), width=1.0, orientation=270, layer='WG_SIN')
    ecl2.add_port(name="o4", center=(-313.55,   79.28), width=1.0, orientation=0,   layer='WG_SIN')
    # Si Ports:
    ecl2.add_port(name="o5", center=(-357.578, -423.474), width=0.5, orientation=0,  layer='WG')
    # Metal 2 Ports:
    ecl2.add_port(name="e1", center=(-1387.26, -53.549), width=26.962, orientation=180,  layer="MT2", port_type="electrical")
    ecl2.add_port(name="e2", center=(-1422.11, -121.891), width=26.962, orientation=180,  layer="MT2", port_type="electrical")
    ecl2.add_port(name="e3", center=(-577.67, -40.239), width=20, orientation=90,  layer="MT2", port_type="electrical")
    ecl2.add_port(name="e4", center=(-544.2, -108.325), width=20, orientation=90,  layer="MT2", port_type="electrical")
    ecl2.add_port(name="e5", center=(-575.05, -452.1), width=20, orientation=270,  layer="MT2", port_type="electrical")
    ecl2.add_port(name="e6", center=(-473.82, -469.5), width=20, orientation=270,  layer="MT2", port_type="electrical")
    ecl2.add_port(name="e7", center=(-304.26, -319.93), width=20, orientation=0,  layer="MT2", port_type="electrical")
    ecl2.add_port(name="e8", center=(-303.29, 20.07), width=20, orientation=0,  layer="MT2", port_type="electrical")

    ecl2 = c.add_ref(ecl2)
    ecl2.xmin = die.xmin - 6
    ecl2.movey(0)

    #----- Heaters Electrical Routing----------
    first_pad = 19 # the firs pad on the left
    gf.routing.route_single(
    c,
    port1 = ecl2.ports['e2'],
    port2 = pads[first_pad].ports['e4'],
    cross_section = "metal_routing",
    waypoints = [
            (float(ecl2.ports['e2'].center[0] - 40), float(ecl2.ports['e2'].center[1])),
            (float(ecl2.ports['e2'].center[0] - 40), float(ecl2.ymax + 40)),
            (float(ecl2.xmax + 280), float(ecl2.ymax + 40)),
            (float(ecl2.xmax + 280), float(pads[first_pad].ports['e4'].center[1] - 150)),
            (float(pads[first_pad].ports['e4'].center[0]), float(pads[first_pad].ports['e4'].center[1] - 150)),
            
    ],
    )
    gf.routing.route_single(
        c,
        port1 = ecl2.ports['e1'],
        port2 = pads[first_pad+1].ports['e4'],
        cross_section = "metal_routing",
        waypoints = [
            (float(ecl2.ports['e1'].center[0] - 40), float(ecl2.ports['e1'].center[1])),
            (float(ecl2.ports['e1'].center[0] - 40), float(ecl2.ymax + 20)),
            (float(ecl2.xmax + 300), float(ecl2.ymax + 20)),
            (float(ecl2.xmax + 300), float(pads[first_pad].ports['e4'].center[1] - 170)),
            (float(pads[first_pad + 1].ports['e4'].center[0]), float(pads[first_pad].ports['e4'].center[1] - 170)),
            
        ],
    )
    gf.routing.route_single(
        c,
        port1 = ecl2.ports['e3'],
        port2 = pads[first_pad+1].ports['e4'],
        cross_section = "metal_routing",
        waypoints = [
            (float(ecl2.ports['e3'].center[0]), float(ecl2.ymax + 20)),
            (float(ecl2.xmax + 300), float(ecl2.ymax + 20)),
            (float(ecl2.xmax + 300), float(pads[first_pad].ports['e4'].center[1] - 170)),
            (float(pads[first_pad + 1].ports['e4'].center[0]), float(pads[first_pad].ports['e4'].center[1] - 170)),
        ],
    )

    gf.routing.route_single(
        c,
        port1 = ecl2.ports['e4'],
        port2 = pads[first_pad+2].ports['e4'],
        cross_section = "metal_routing",
        waypoints = [
            # (float(ecl2.ports['e4'].center[0]), float(ecl2.ymax)),
            # (float(pads[first_pad].ports['e4'].center[0] + 40), float(ecl2.ymax )),
            # (float(pads[first_pad].ports['e4'].center[0] + 40), float(pads[first_pad].ports['e4'].center[1] - 60)),
            # (float(pads[first_pad+2].ports['e4'].center[0]), float(pads[first_pad].ports['e4'].center[1] - 60)),
            (float(ecl2.ports['e4'].center[0]), float(ecl2.ymax)),
            (float(ecl2.xmax + 320), float(ecl2.ymax )),
            (float(ecl2.xmax + 320), float(pads[first_pad].ports['e4'].center[1] - 190)),
            (float(pads[first_pad + 2].ports['e4'].center[0]), float(pads[first_pad].ports['e4'].center[1] - 190)),
        ],
    )
    gf.routing.route_single(
        c,
        port1 = ecl2.ports['e8'],
        port2 = pads[first_pad+3].ports['e4'],
        cross_section = "metal_routing",
        waypoints = [
            (float(ecl2.ports['e8'].center[0] + 20), float(ecl2.ports['e8'].center[1])),
            (float(ecl2.ports['e8'].center[0] + 20), float(ecl2.ymax - 20)),
            (float(ecl2.xmax + 340), float(ecl2.ymax - 20)),
            (float(ecl2.xmax + 340), float(pads[first_pad].ports['e4'].center[1] - 210)),
            (float(pads[first_pad+3].ports['e4'].center[0]), float(pads[first_pad].ports['e4'].center[1] - 210)),
        ],
    )
    gf.routing.route_single(
        c,
        port1 = ecl2.ports['e7'],
        port2 = pads[first_pad+4].ports['e4'],
        cross_section = "metal_routing",
        waypoints = [
            (float(ecl2.ports['e8'].center[0] + 40), float(ecl2.ports['e7'].center[1])),
            (float(ecl2.ports['e8'].center[0] + 40), float(ecl2.ymax - 40)),
            (float(ecl2.xmax + 360), float(ecl2.ymax - 40)),
            (float(ecl2.xmax + 360), float(pads[first_pad].ports['e4'].center[1] - 230)),
            (float(pads[first_pad+4].ports['e4'].center[0]), float(pads[first_pad].ports['e4'].center[1] - 230)),
        ],
    )
    gf.routing.route_single(
        c,
        port1 = ecl2.ports['e6'],
        port2 = pads[first_pad+4].ports['e4'],
        cross_section = "metal_routing",
        waypoints = [
            (float(ecl2.ports['e6'].center[0]), float(ecl2.ports['e6'].center[1] -20)),
            (float(ecl2.ports['e8'].center[0] + 60), float(ecl2.ports['e6'].center[1] -20)),
            (float(ecl2.ports['e8'].center[0] + 60), float(ecl2.ymax - 60)),
            (float(ecl2.xmax + 360), float(ecl2.ymax - 60)),
            (float(ecl2.xmax + 360), float(pads[first_pad].ports['e4'].center[1] - 230)),
            (float(pads[first_pad+4].ports['e4'].center[0]), float(pads[first_pad].ports['e4'].center[1] - 230)),
        ],
    )
    gf.routing.route_single(
        c,
        port1 = ecl2.ports['e5'],
        port2 = pads[first_pad+5].ports['e4'],
        cross_section = "metal_routing",
        waypoints = [
            (float(ecl2.ports['e5'].center[0]), float(ecl2.ports['e6'].center[1] -40)),
            (float(ecl2.ports['e8'].center[0] + 80), float(ecl2.ports['e6'].center[1] -40)),
            (float(ecl2.ports['e8'].center[0] + 80), float(ecl2.ymax - 80)),
            (float(ecl2.xmax + 380), float(ecl2.ymax - 80)),
            (float(ecl2.xmax + 380), float(pads[first_pad].ports['e4'].center[1] - 250)),
            (float(pads[first_pad+5].ports['e4'].center[0]), float(pads[first_pad].ports['e4'].center[1] - 250)),
        ],
    )

    # ----------- PDs -----------------
    pd12 = c.add_ref(Balanced_PD())
    pd12.xmin = pads[first_pad + 6].ports['e1'].center[0]
    pd12.ymax = pads[first_pad + 6].ports['e2'].center[1]

    pd34 = c.add_ref(Balanced_PD())
    pd34.xmin = pads[first_pad + 9].ports['e1'].center[0]
    pd34.ymax = pads[first_pad + 9].ports['e2'].center[1]

    # ------------- Optical routings---------------
    ecl2_via1 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    ecl2_via1.mirror_x()
    ecl2_via1.xmin = ecl2.ports['e8'].center[0] + 100
    ecl2_via1.movey(ecl2.ports['o4'].center[1])
    ecl2_via1_mmi = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    ecl2_via1_mmi.move(ecl2_via1.ports['o1'].center)

    ecl2_via2 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    ecl2_via2.mirror_x()
    ecl2_via2.xmin = ecl2.ports['e8'].center[0] + 100
    ecl2_via2.movey(ecl2.ports['o4'].center[1] - 50)
    ecl2_via2_mmi = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    ecl2_via2_mmi.move(ecl2_via2.ports['o1'].center)

    ecl2_via3 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    ecl2_via3.mirror_x()
    ecl2_via3.xmin = ecl2.ports['e8'].center[0] + 100
    ecl2_via3.movey(ecl2.ports['o4'].center[1] - 100)
    ecl2_via3_mmi = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    ecl2_via3_mmi.move(ecl2_via3.ports['o1'].center)

    ecl2_via4 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    ecl2_via4.mirror_x()
    ecl2_via4.xmin = ecl2.ports['e8'].center[0] + 100
    ecl2_via4.movey(ecl2.ports['o4'].center[1] - 150)
    ecl2_via4_mmi = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    ecl2_via4_mmi.move(ecl2_via4.ports['o1'].center)

    ecl2_combiner1 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    ecl2_combiner1.mirror_x()
    ecl2_combiner1.xmin = ecl2_via1_mmi.xmax + 20
    ecl2_combiner1.ymax = ecl2_via1_mmi.ymin - 15

    # SiN routings

    gf.routing.route_single(
        c,
        port1 = ecl2.ports['o4'],
        port2 = ecl2_via1.ports['o2'],
        cross_section = xs_sin,
    )

    gf.routing.route_single(
        c,
        port1 = ecl2.ports['o3'],
        port2 = ecl2_via2.ports['o2'],
        cross_section = xs_sin,
        waypoints = [
            (float(ecl2.ports['o3'].center[0]) , float(ecl2.ymin - 10)),
            (float(ecl2.xmax + 30) , float(ecl2.ymin - 10)),
            (float(ecl2.xmax + 30) , float(ecl2_via2.ports['o2'].center[1])),
        ],
    )

    gf.routing.route_single(
        c,
        port1 = ecl2.ports['o2'],
        port2 = ecl2_via3.ports['o2'],
        cross_section = xs_sin,
        waypoints = [
            (float(ecl2.ports['o2'].center[0] - 50) , float(ecl2.ports['o2'].center[1])),
            (float(ecl2.ports['o2'].center[0] - 50) , float(ecl2.ymin - 15)),
            (float(ecl2.xmax + 35) , float(ecl2.ymin - 15)),
            (float(ecl2.xmax + 35) , float(ecl2_via3.ports['o2'].center[1])),
        ],
    )

    gf.routing.route_single(
        c,
        port1 = ecl2.ports['o1'],
        port2 = ecl2_via4.ports['o2'],
        cross_section = xs_sin,
        waypoints = [
            (float(ecl2.ports['o1'].center[0] - 55) , float(ecl2.ports['o1'].center[1])),
            (float(ecl2.ports['o1'].center[0] - 55) , float(ecl2.ymin - 20)),
            (float(ecl2.xmax + 40) , float(ecl2.ymin - 20)),
            (float(ecl2.xmax + 40) , float(ecl2_via4.ports['o2'].center[1])),
        ],
    )

    # Si routings

    gf.routing.route_single(
        c,
        port1 = ecl2_via1_mmi.ports['o3'],
        port2 = ecl2_combiner1.ports['o2'],
        cross_section = 'strip',
    )

    gf.routing.route_single(
        c,
        port1 = ecl2_via4_mmi.ports['o2'],
        port2 = ecl2_combiner1.ports['o3'],
        cross_section = 'strip',
        waypoints = [
            (float(ecl2_via4_mmi.ports['o2'].center[0] + 10), float(ecl2_via4_mmi.ports['o2'].center[1])),
            (float(ecl2_via4_mmi.ports['o2'].center[0] + 10), float(ecl2_via4_mmi.ports['o2'].center[1] + 20)),
            (float(ecl2_via4.ports['o2'].center[0] - 40), float(ecl2_via4_mmi.ports['o2'].center[1] + 20)),
            (float(ecl2_via4.ports['o2'].center[0] - 40), float(ecl2_combiner1.ports['o3'].center[1])),
        ],
    )

    gf.routing.route_single(
        c,
        port1 = ecl2_via1_mmi.ports['o2'],
        port2 = pd34.ports['o2'],
        cross_section = 'strip',
        waypoints = [
            (float(ecl2_via1_mmi.ports['o2'].center[0] + 30), float(ecl2_via1_mmi.ports['o2'].center[1])),
            (float(ecl2_via1_mmi.ports['o2'].center[0] + 30), float(pd34.ports['o2'].center[1] - 60)),
            (float(pd34.ports['o2'].center[0]), float(pd34.ports['o2'].center[1] - 60)),
        ],
    )

    gf.routing.route_single(
        c,
        port1 = ecl2_via4_mmi.ports['o3'],
        port2 = pd34.ports['o1'],
        cross_section = 'strip',
        waypoints = [
            (float(ecl2_via4_mmi.ports['o3'].center[0] + 10), float(ecl2_via4_mmi.ports['o3'].center[1])),
            (float(ecl2_via4_mmi.ports['o3'].center[0] + 10), float(ecl2_via4_mmi.ports['o3'].center[1] - 20)),
            (float(ecl2_via4.ports['o2'].center[0] - 45), float(ecl2_via4_mmi.ports['o3'].center[1] - 20)),
            (float(ecl2_via4.ports['o2'].center[0] - 45), float(ecl2_via1_mmi.ports['o2'].center[1] + 10)),
            (float(ecl2_via1_mmi.ports['o2'].center[0] + 25), float(ecl2_via1_mmi.ports['o2'].center[1] + 10)),
            (float(ecl2_via1_mmi.ports['o2'].center[0] + 25), float(pd34.ports['o2'].center[1] - 55)),
            (float(pd34.ports['o1'].center[0]), float(pd34.ports['o2'].center[1] - 55)),
        ],
    )

    gf.routing.route_single(
        c,
        port1 = ecl2_via2_mmi.ports['o3'],
        port2 = pd12.ports['o2'],
        cross_section = 'strip',
        waypoints = [
            (float(ecl2_via2_mmi.ports['o3'].center[0] + 10), float(ecl2_via2_mmi.ports['o3'].center[1])),
            (float(ecl2_via2_mmi.ports['o3'].center[0] + 10), float(ecl2_via2_mmi.ports['o3'].center[1] - 20)),
            (float(ecl2_via2.ports['o2'].center[0] - 35), float(ecl2_via2_mmi.ports['o3'].center[1] - 20)),
            (float(ecl2_via4.ports['o2'].center[0] - 35), float(ecl2_via3_mmi.ports['o2'].center[1] - 15)),
            (float(ecl2_via3_mmi.ports['o2'].center[0] + 15), float(ecl2_via3_mmi.ports['o2'].center[1] - 15)),
            (float(ecl2_via3_mmi.ports['o2'].center[0] + 15), float(ecl2_via4_mmi.ports['o2'].center[1] - 30)),
            (float(ecl2_via4.ports['o2'].center[0] - 50), float(ecl2_via4_mmi.ports['o2'].center[1] - 30)),
            (float(ecl2_via4.ports['o2'].center[0] - 50), float(ecl2_via1_mmi.ports['o2'].center[1] + 15)),
            (float(ecl2_via1_mmi.ports['o2'].center[0] + 20), float(ecl2_via1_mmi.ports['o2'].center[1] + 15)),
            (float(ecl2_via1_mmi.ports['o2'].center[0] + 20), float(pd34.ports['o2'].center[1] - 50)),
            (float(pd12.ports['o2'].center[0]), float(pd34.ports['o2'].center[1] - 50)),
        ],
    )

    gf.routing.route_single(
        c,
        port1 = ecl2_via3_mmi.ports['o3'],
        port2 = pd12.ports['o1'],
        cross_section = 'strip',
        waypoints = [
            (float(ecl2_via3_mmi.ports['o3'].center[0] + 20), float(ecl2_via3_mmi.ports['o3'].center[1])),
            (float(ecl2_via2_mmi.ports['o3'].center[0] + 20), float(ecl2_via4_mmi.ports['o3'].center[1] - 35)),
            (float(ecl2_via2.ports['o2'].center[0] - 55), float(ecl2_via4_mmi.ports['o3'].center[1] - 35)),
            (float(ecl2_via4.ports['o2'].center[0] - 55), float(ecl2_via1_mmi.ports['o2'].center[1] + 20)),
            (float(ecl2_via1_mmi.ports['o2'].center[0] + 15), float(ecl2_via1_mmi.ports['o2'].center[1] + 20)),
            (float(ecl2_via1_mmi.ports['o2'].center[0] + 15), float(pd34.ports['o2'].center[1] - 45)),
            (float(pd12.ports['o1'].center[0]), float(pd34.ports['o2'].center[1] - 45)),
        ],
    )

    #-----------------output vias
    via_out = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via_out.rotate(90)
    via_out.xmin = ecl2_combiner1.xmax + 40
    via_out.ymin = ecl2_combiner1.ymax + 50

    gf.routing.route_single(
        c,
        port1 = ecl2_combiner1.ports['o1'],
        port2 = via_out.ports['o1'],
        cross_section = 'strip',
    )


    via_out2 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via_out2.rotate(-90)
    via_out2.xmin = ecl2_via3_mmi.xmax + 40
    via_out2.ymax = ecl2_via3_mmi.ymin - 20

    via_out3 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via_out3.rotate(-90)
    via_out3.xmin = ecl2_via3_mmi.xmax + 50
    via_out3.ymax = ecl2_via3_mmi.ymin - 20

    via_out22 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via_out22.xmin = ecl2.x 
    via_out22.ymax = ecl2.ymin - 60

    via_out33 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via_out33.xmin = ecl2.x 
    via_out33.ymax = ecl2.ymin - 70

    gf.routing.route_single(
        c,
        port1 = ecl2_via3_mmi.ports['o2'],
        port2 = via_out2.ports['o1'],
        cross_section = 'strip',
    )
    gf.routing.route_single(
        c,
        port1 = ecl2_via2_mmi.ports['o2'],
        port2 = via_out3.ports['o1'],
        cross_section = 'strip',
    )

    gf.routing.route_single(
        c,
        port1 = via_out2.ports['o2'],
        port2 = via_out22.ports['o2'],
        cross_section = xs_sin,
    )
    gf.routing.route_single(
        c,
        port1 = via_out3.ports['o2'],
        port2 = via_out33.ports['o2'],
        cross_section = xs_sin,
    )

    c.add_port('o1', port = via_out22.ports['o1'])
    c.add_port('o2', port = via_out33.ports['o1'])
    c.add_port('o3', port = via_out.ports['o2'])
    c.add_port('o4', port = ecl2.ports['o5'])
   
    return c
