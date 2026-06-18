import gdsfactory as gf
from gdsfactory.pdk import get_active_pdk
from amf.chp.tech import LAYER, TECH

from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_LSiN2SOISSC_Cband_v5p0,)
from amf.config import PATH
# from amf.chp.tech import LAYER, TECH
from amf.import_gds import import_gds

from .Delay_Spiral import Delay_Spiral
from .MZI_Ring import MZI_Ring
from .Rings_Pack import Rings_Pack
from .MZIs_Pack import MZIs_Pack
from .MZIs_Pack4 import *
from .Balanced_PD import Balanced_PD
from .Wavemeter import Wavemeter
from .ECL_to_WL import ECL_to_WL
from .ECL1 import ECL1
from .ECL2 import ECL2
from .ECL3 import ECL3
from .SiN_MZI import SiN_MZI
from .SiN_1250_MZI import SiN_1250_MZI
from .Rib_MZI import Rib_MZI
from .strip_MZI import strip_MZI
from .via_MZI import via_MZI

gdsdir = PATH.gds_chp

N_FIBERS = 22
PITCH = 127.0  # um
DIE_SIZE = (7400, 3000)


@gf.cell
def Main() -> gf.Component:
    c = gf.Component()
    pdk = get_active_pdk()

    die = c.add_ref(gf.components.rectangle(size=DIE_SIZE, layer = LAYER.MARKER))
    die.move((-3700, -1500))
    # routing SiN with bending radius of 45 um
    xs_sin = gf.cross_section.strip(
    width= 1,
    radius=45,
    radius_min=45,
    layer=LAYER.WG_SIN,
    )

    # Load the AMF SiN edge coupler fixed cell
    sin_ec = pdk.get_component("AMF_300LSOI_LSiNEdgeCoupler_Cband_v5p0")

    # Place 20 copies on the right (east) side, vertically centered on the die
    # Array spans (N_FIBERS - 1) * PITCH; center it vertically
    array_height = (N_FIBERS - 1) * PITCH
    y_start = die.ymin + (DIE_SIZE[1] - array_height) / 2 

    refs = []
    for i in range(N_FIBERS):
        ec = c.add_ref(sin_ec)
        # opt_2_sin (fiber port, East) flush to die right edge
        ec.xmax = die.xmax 
        ec.y = y_start + i * PITCH
        refs.append(ec)
        # Expose on-chip port (o1, West) as e1..e20
        c.add_port(name=f"e{i + 1}", port=ec.ports["o1"])

    # Connect first two (e1 <-> e2) and last two (e19 <-> e20) as loopbacks
    gf.routing.route_single(
        c,
        port1=refs[0].ports["o1"],
        port2=refs[1].ports["o1"],
        cross_section=xs_sin,
    )
    gf.routing.route_single(
        c,
        port1=refs[-2].ports["o1"],
        port2=refs[-1].ports["o1"],
        cross_section=xs_sin,
    )


    #---------------------------------------------------------------------------------------
    # RINGS
    #---------------------------------------------------------------------------------------
    # Rings = c.add_ref(Rings_Pack())
    # Rings.move((-1000, 1000))

    

    
    #---------------------------------------------------------------------------------------
    # ECLs 
    #---------------------------------------------------------------------------------------
    #------------ ECL2 ------------------
    ecl1 = c.add_ref(ECL1())

    # routings
    gf.routing.route_single(
        c,
        port1 = ecl1.ports['o1'],
        port2 = refs[16].ports['o1'],
        cross_section = xs_sin,
        waypoints = [
            (float(ecl1.ports['o1'].center[0] + 250), float(ecl1.ports['o1'].center[1])),
            (float(ecl1.ports['o1'].center[0] + 250), die.ymax - 140),
            (float(refs[16].ports['o1'].center[0] -120), die.ymax - 140),
            (float(refs[16].ports['o1'].center[0] -120), float(refs[16].ports['o1'].center[1])),
        ]
    )

    gf.routing.route_single(
        c,
        port1 = ecl1.ports['o2'],
        port2 = refs[17].ports['o1'],
        cross_section = xs_sin,
        waypoints = [
            (float(ecl1.ports['o2'].center[0]), die.ymax - 130),
            (float(refs[16].ports['o1'].center[0] -110), die.ymax - 130),
            (float(refs[16].ports['o1'].center[0] -110), float(refs[17].ports['o1'].center[1])),
        ]
    )
    gf.routing.route_single(
        c,
        port1 = ecl1.ports['o3'],
        port2 = refs[18].ports['o1'],
        cross_section = xs_sin,
        waypoints = [
            (float(ecl1.ports['o3'].center[0]), die.ymax - 120),
            (float(refs[18].ports['o1'].center[0] -100), die.ymax - 120),
            (float(refs[18].ports['o1'].center[0] -100), float(refs[18].ports['o1'].center[1])),
        ]
    )
    gf.routing.route_single(
        c,
        port1 = ecl1.ports['o4'],
        port2 = refs[19].ports['o1'],
        cross_section = xs_sin,
        waypoints = [
            (float(ecl1.ports['o4'].center[0]), die.ymax - 110),
            (float(refs[19].ports['o1'].center[0] -90), die.ymax - 110),
            (float(refs[19].ports['o1'].center[0] -90), float(refs[19].ports['o1'].center[1])),
        ]
    )
    
    #------------ ECL2 ------------------
    ecl2 = c.add_ref(ECL2())

    #------------ ECL3 ------------------
    ecl3 = c.add_ref(ECL3())
    

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

    # ---------------Bottom PADS:------------
    N_bPADS = 55
    bPAD_PITCH = 125.0
    pad_cell = pdk.get_component("pad")

    bpads = []
    x_start = die.xmin + 150  #die.x - (N_PADS - 1) * PAD_PITCH / 2 + 1400
    for i in range(N_bPADS):
        p = c.add_ref(pad_cell)
        p.x = x_start + i * bPAD_PITCH
        p.ymin = die.ymin + 50
        bpads.append(p)

    #---------------------------------------------------------------------------------------
    # ECL to WL
    #---------------------------------------------------------------------------------------
    ecl2wl = c.add_ref(ECL_to_WL())
    ecl2wl.ymin = die.ymin +300
    ecl2wl.xmin = die.xmin + 1700

    #----------- Electrical routings--------
    gf.routing.route_bundle(
        c,
        ports1 = [ecl2wl.ports['e1'], ecl2wl.ports['e2']],
        ports2 = [bpads[15].ports['e2'], bpads[16].ports['e2']],
        cross_section= 'metal_routing',   
    )

    gf.routing.route_single(
        c,
        port1 = ecl2wl.ports['e4'],
        port2 = bpads[17].ports['e2'],
        cross_section= 'metal_routing',   
    )

    gf.routing.route_single(
        c,
        port1 = ecl2wl.ports['e3'],
        port2 = bpads[18].ports['e2'],
        cross_section= 'metal_routing',
        waypoints = [
            (float(ecl2wl.ports['e3'].center[0]), float(ecl2wl.ports['e3'].center[1] + 20)),
            (float(ecl2wl.ports['e3'].center[0] + 120), float(ecl2wl.ports['e3'].center[1] + 20)),
            (float(ecl2wl.ports['e3'].center[0] + 120), float(ecl2wl.ports['e3'].center[1] -80)),
            (float(bpads[18].ports['e2'].center[0]), float(ecl2wl.ports['e3'].center[1] -80)),
        ],   
    )

    gf.routing.route_bundle(
        c,
        ports1 = [ecl2wl.ports['e5'], ecl2wl.ports['e6']],
        ports2 = [bpads[19].ports['e2'], bpads[20].ports['e2']],
        cross_section= 'metal_routing',   
    )
  
    # ECL 3 to ECL to WL
    gf.routing.route_single(
        c,
        port1 = ecl3.ports['o4'],
        port2 = ecl2wl.ports['o1'],
        cross_section = 'strip',
        waypoints = [
            (float(ecl3.ports['o4'].center[0] + 310), float(ecl3.ports['o4'].center[1])),
            (float(ecl3.ports['o4'].center[0] + 310), float(ecl2wl.ports['o1'].center[1])),
        ],
    )

    # ECL 2 to ECL to WL
    gf.routing.route_single(
        c,
        port1 = ecl2.ports['o4'],
        port2 = ecl2wl.ports['o2'],
        cross_section = 'strip',
        waypoints = [
            (float(ecl3.ports['o4'].center[0] + 315), float(ecl2.ports['o4'].center[1])),
            (float(ecl3.ports['o4'].center[0] + 315), float(ecl2wl.ports['o2'].center[1])),
        ],
    )
    #---------------------------------------------------------------------------------------
    # SPIRAL
    #---------------------------------------------------------------------------------------
    spiral = c.add_ref(Delay_Spiral(width = 3, taper_length = 200, min_bend_radius=270, separation=6.5, number_of_loops=48, npoints=20000,))
    spiral.mirror_y()
    spiral.move((350 , die.ymin - spiral.ymin + 500))  # 200 µm from left edge, vertically centered
    
    gf.routing.route_single(
        c,
        port1 = ecl2wl.ports['o4'],
        port2 = spiral.ports['o1'],
        cross_section = 'strip',
        waypoints = [
            (float(ecl2wl.ports['o4'].center[0] + 10), float(ecl2wl.ports['o4'].center[1])),
            (float(ecl2wl.ports['o4'].center[0] + 10), float(die.ymin + 160)),
            (float(ecl2wl.ports['o4'].center[0] + 900), float(die.ymin + 160)),
            (float(ecl2wl.ports['o4'].center[0] + 900), float(spiral.ports['o1'].center[1] -60)),
            (float(spiral.ports['o1'].center[0] -10), float(spiral.ports['o1'].center[1] -60)),
            (float(spiral.ports['o1'].center[0] -10), float(spiral.ports['o1'].center[1])),
        ],
    )

    gf.routing.route_single(
        c,
        port1 = spiral.ports['e1'],
        port2 = bpads[34].ports['e2'],
        cross_section = 'metal_routing',
        waypoints = [
            (float(spiral.ports['e1'].center[0]), float(bpads[34].ports['e2'].center[1] + 300)),
            (float(bpads[34].ports['e2'].center[0]), float(bpads[34].ports['e2'].center[1] + 300)),
        ],

    )
    gf.routing.route_single(
        c,
        port1 = spiral.ports['e2'],
        port2 = bpads[33].ports['e2'],
        cross_section = 'metal_routing',
        waypoints = [
            (float(spiral.ports['e2'].center[0]), float(bpads[33].ports['e2'].center[1] + 260)),
            (float(bpads[33].ports['e2'].center[0]), float(bpads[33].ports['e2'].center[1] + 260)),
        ],

    )

    gf.routing.route_bundle(
        c,
        ports1 = [spiral.ports['e4'], spiral.ports['e3']],
        ports2 = [bpads[35].ports['e2'], bpads[36].ports['e2']],
        cross_section = 'metal_routing',
    )

    gf.routing.route_bundle(
        c,
        ports1 = [spiral.ports['e5'], spiral.ports['e6'], spiral.ports['e7']],
        ports2 = [bpads[37].ports['e2'], bpads[38].ports['e2'], bpads[39].ports['e2']],
        cross_section = 'metal_routing',
    )

    bpd_spiral = c.add_ref(Balanced_PD())
    bpd_spiral.mirror_y()
    bpd_spiral.xmin = bpads[40].ports['e1'].center[0]
    bpd_spiral.ymin = bpads[40].ports['e4'].center[1]

    gf.routing.route_bundle(
        c,
        ports1 = [spiral.ports['o2'], spiral.ports['o3']],
        ports2 = [bpd_spiral.ports['o1'], bpd_spiral.ports['o2']],
        cross_section = 'strip',
    )
    #---------------------------------------------------------------------------------------
    # WL with Ring
    #---------------------------------------------------------------------------------------
    wl_ring = c.add_ref(MZI_Ring(l = 580, gap = 0.35, coupling_length = 30, coupling_radius = 50, wg_width = 1.25, taper_length = 50, separation = 5.25, min_bend_radius= 100, htr_length = 100, number_of_loops = 43, npoints = 20000,))
    wl_ring.move((-1400 , die.ymin - wl_ring.ymin + 420))

    gf.routing.route_single(
        c,
        port1 = ecl2wl.ports['o3'],
        port2 = wl_ring.ports['o1'],
        cross_section = 'strip',
        waypoints = [
            (float(ecl2wl.ports['o3'].center[0] + 10), float(ecl2wl.ports['o3'].center[1])),
            (float(ecl2wl.ports['o3'].center[0] + 10), float(ecl2wl.ports['o3'].center[1] + 70)),
            (float(wl_ring.ports['o1'].center[0] - 10), float(ecl2wl.ports['o3'].center[1] + 70)),
            (float(wl_ring.ports['o1'].center[0] - 10), float(wl_ring.ports['o1'].center[1] )),
        ],
    )

    gf.routing.route_bundle(
        c,
        ports1 = [wl_ring.ports['e4'], wl_ring.ports['e3']],
        ports2 = [bpads[21].ports['e2'], bpads[22].ports['e2']],
        cross_section = 'metal_routing',
    )

    gf.routing.route_single(
        c,
        port1 = wl_ring.ports['e2'],
        port2 = bpads[23].ports['e2'],
        cross_section = 'metal_routing',
        waypoints = [
            (float( wl_ring.ports['e2'].center[0]), float( wl_ring.ports['e1'].center[1] - 260)),
            (float( bpads[23].ports['e2'].center[0]), float( wl_ring.ports['e1'].center[1] - 260)),
        ] 
    )

    gf.routing.route_single(
        c,
        port1 = wl_ring.ports['e1'],
        port2 = bpads[24].ports['e2'],
        cross_section = 'metal_routing',
        waypoints = [
            (float( wl_ring.ports['e1'].center[0]), float( wl_ring.ports['e1'].center[1] - 240)),
            (float( bpads[24].ports['e2'].center[0]), float( wl_ring.ports['e1'].center[1] - 240)),
        ] 
    )

    bpd_wl_ring = c.add_ref(Balanced_PD())
    bpd_wl_ring.mirror_y()
    bpd_wl_ring.xmin = bpads[25].ports['e1'].center[0]
    bpd_wl_ring.ymin = bpads[25].ports['e4'].center[1]

    gf.routing.route_single(
        c,
        port1 = wl_ring.ports['o3'],
        port2 = bpd_wl_ring.ports['o1'],
        cross_section = 'strip',
        waypoints = [
            (float(wl_ring.ports['o3'].center[0] + 10), float(wl_ring.ports['o3'].center[1])),
            (float(wl_ring.ports['o3'].center[0] + 10), float(bpd_wl_ring.ports['o1'].center[1] + 20)),
            (float(bpd_wl_ring.ports['o1'].center[0] ), float(bpd_wl_ring.ports['o1'].center[1] + 20)),
        ],  
    )
    gf.routing.route_single(
        c,
        port1 = wl_ring.ports['o2'],
        port2 = bpd_wl_ring.ports['o2'],
        cross_section = 'strip',  
        waypoints = [
            (float(wl_ring.ports['o2'].center[0] + 15), float(wl_ring.ports['o2'].center[1])),
            (float(wl_ring.ports['o2'].center[0] + 15), float(bpd_wl_ring.ports['o2'].center[1] + 25)),
            (float(bpd_wl_ring.ports['o2'].center[0] ), float(bpd_wl_ring.ports['o2'].center[1] + 25)),
        ],
    )
    # ---------------------------------------------------------------------------------------
    # Balanced PD
    #---------------------------------------------------------------------------------------
    # balanced_pd = c.add_ref(Balanced_PD())
    # balanced_pd.move((-2000, -1000))
   
    #---------------------------------------------------------------------------------------
    # Wavemeter
    #---------------------------------------------------------------------------------------
    wavemeter = c.add_ref(Wavemeter())
    wavemeter.ymax = die.ymax - 50
    wavemeter.xmin = die.x + 275

    #---------------------------------------------------------------------------------------
    # MZIs first set
    #---------------------------------------------------------------------------------------
    mzi_pack1 = c.add_ref(MZIs_Pack())
    mzi_pack1.xmin = bpads[44].ports['e1'].center[0]
    mzi_pack1.ymax = spiral.ymin + 100

    #---------- Connecting ECL2 and MZI and Outputs

    ecl3_via_out_top = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    ecl3_via_out_top.rotate(-90)
    ecl3_via_out_top.ymin = bpads[11].ymax + 100
    ecl3_via_out_top.xmax = bpads[12].xmin

    gf.routing.route_single(
        c,
        port1 = ecl3.ports['o3'],
        port2 = ecl3_via_out_top.ports['o1'],
        cross_section = 'strip',
    )
    gf.routing.route_single(
        c,
        port1 = ecl3_via_out_top.ports['o2'],
        port2 = refs[2].ports['o1'],
        cross_section = xs_sin,
        waypoints = [
            (float(ecl3_via_out_top.ports['o2'].center[0]), float(bpads[0].ports['e1'].center[1])),
            (float(refs[2].ports['o1'].center[0] - 50), float(bpads[0].ports['e1'].center[1])),
            (float(refs[2].ports['o1'].center[0] - 50), float(refs[2].ports['o1'].center[1])),
        ],
    )

    gf.routing.route_single(
        c,
        port1 = ecl3.ports['o2'],
        port2 = mzi_pack1.ports['o5'],
        cross_section = 'strip',
        waypoints = [
            (float(ecl3.ports['o2'].center[0] + 25), float(ecl3.ports['o2'].center[1])),
            (float(ecl3.ports['o2'].center[0] + 25), float(bpads[0].ports['e2'].center[1] + 140)),
            (float(ecl3.ports['o2'].center[0] + 225), float(bpads[0].ports['e2'].center[1] + 140)),
            (float(ecl3.ports['o2'].center[0] + 225), float(bpads[0].ports['e2'].center[1] - 5)),
            (float(mzi_pack1.ports['o5'].center[0] - 30), float(bpads[0].ports['e2'].center[1] - 5)),
            (float(mzi_pack1.ports['o5'].center[0] - 30), float(mzi_pack1.ports['o5'].center[1])),
        ],
    )
    gf.routing.route_single(
        c,
        port1 = ecl3.ports['o1'],
        port2 = mzi_pack1.ports['o4'],
        cross_section = 'strip',
        waypoints = [
            (float(ecl3.ports['o1'].center[0] + 25), float(ecl3.ports['o1'].center[1])),
            (float(ecl3.ports['o1'].center[0] + 25), float(bpads[0].ports['e2'].center[1] - 10)),
            (float(mzi_pack1.ports['o9'].center[0] + 30), float(bpads[0].ports['e2'].center[1] - 10)),
            (float(mzi_pack1.ports['o9'].center[0] + 30), float(mzi_pack1.ports['o4'].center[1] - 30)),
            (float(mzi_pack1.ports['o4'].center[0] - 30), float(mzi_pack1.ports['o4'].center[1] - 30)),
            (float(mzi_pack1.ports['o4'].center[0] - 30), float(mzi_pack1.ports['o4'].center[1] )),
        ],
    )

    gf.routing.route_single(
        c,
        port1 = mzi_pack1.ports['o9'],
        port2 = refs[4].ports['o1'], 
        cross_section = xs_sin,
        waypoints = [
            (float(refs[4].ports['o1'].center[0] -60), float(mzi_pack1.ports['o9'].center[1])),
            (float(refs[4].ports['o1'].center[0] -60), float(refs[4].ports['o1'].center[1])),
        ],
    )
    gf.routing.route_single(
        c,
        port1 = mzi_pack1.ports['o8'],
        port2 = refs[5].ports['o1'], 
        cross_section = xs_sin,
        waypoints = [
            (float(refs[5].ports['o1'].center[0] -70), float(mzi_pack1.ports['o8'].center[1])),
            (float(refs[5].ports['o1'].center[0] -70), float(refs[5].ports['o1'].center[1])),
        ],
    )
    gf.routing.route_single(
        c,
        port1 = mzi_pack1.ports['o7'],
        port2 = refs[6].ports['o1'], 
        cross_section = xs_sin,
        waypoints = [
            (float(refs[6].ports['o1'].center[0] -80), float(mzi_pack1.ports['o7'].center[1])),
            (float(refs[6].ports['o1'].center[0] -80), float(refs[6].ports['o1'].center[1])),
        ],
    )

    gf.routing.route_single(
        c,
        port1 = mzi_pack1.ports['o6'],
        port2 = refs[7].ports['o1'], 
        cross_section = xs_sin,
        waypoints = [
            (float(refs[7].ports['o1'].center[0] -90), float(mzi_pack1.ports['o6'].center[1])),
            (float(refs[7].ports['o1'].center[0] -90), float(refs[7].ports['o1'].center[1])),
        ],
    )

    gf.routing.route_single(
        c,
        port1 = mzi_pack1.ports['o10'],
        port2 = refs[8].ports['o1'], 
        cross_section = xs_sin,
        waypoints = [
            (float(mzi_pack1.ports['o10'].center[0] - 50), float(mzi_pack1.ports['o10'].center[1])),
            (float(mzi_pack1.ports['o10'].center[0] - 50), mzi_pack1.ymax + 10),
            (float(refs[8].ports['o1'].center[0] -100), mzi_pack1.ymax + 10),
            (float(refs[8].ports['o1'].center[0] -100), float(refs[8].ports['o1'].center[1])),
        ],
    )

    gf.routing.route_single(
        c,
        port1 = ecl2.ports['o2'],
        port2 = mzi_pack1.ports['o3'],
        cross_section = 'strip',
        waypoints = [
            (float(ecl2.ports['o2'].center[0]) - 500, float(ecl2.ports['o2'].center[1])),
            (float(ecl2.ports['o2'].center[0]) - 500, float(bpads[0].ports['e1'].center[1] - 10)),
            (float(mzi_pack1.ports['o3'].center[0]) - 20, float(bpads[0].ports['e1'].center[1] - 10)),
            (float(mzi_pack1.ports['o3'].center[0]) - 20, float(mzi_pack1.ports['o3'].center[1])),
        ]
    )

    gf.routing.route_single(
        c,
        port1 = ecl2.ports['o1'],
        port2 = mzi_pack1.ports['o2'],
        cross_section = 'strip',
        waypoints = [
            (float(ecl2.ports['o1'].center[0]) - 510, float(ecl2.ports['o1'].center[1])),
            (float(ecl2.ports['o1'].center[0]) - 510, float(bpads[0].ports['e1'].center[1] - 20)),
            (float(mzi_pack1.ports['o2'].center[0]) + 100, float(bpads[0].ports['e1'].center[1] - 20)),
            (float(mzi_pack1.ports['o2'].center[0]) + 100, float(mzi_pack1.ports['o2'].center[1]) - 20),
            (float(mzi_pack1.ports['o2'].center[0]) + -20, float(mzi_pack1.ports['o2'].center[1]) - 20),
            (float(mzi_pack1.ports['o2'].center[0]) + -20, float(mzi_pack1.ports['o2'].center[1])),
        ]
    )

    #---------------------------------------------------------------------------------------
    # MZIs second set
    #---------------------------------------------------------------------------------------
    mzi_pack2 = c.add_ref(MZIs_Pack())
    mzi_pack2.rotate(90)
    mzi_pack2.xmax = die.xmax - 370
    mzi_pack2.ymin = mzi_pack1.ymax + 110

    #---------- Routing -------------------
    gf.routing.route_single(
        c,
        port1 = mzi_pack2.ports['o10'],
        port2 = refs[9].ports['o1'],
        cross_section = xs_sin,
        waypoints = [
            (float(mzi_pack2.ports['o10'].center[0]), float(mzi_pack2.ports['o10'].center[1]) - 60),
            (float(refs[9].ports['o1'].center[0] - 110), float(mzi_pack2.ports['o10'].center[1] -60 )),
            (float(refs[9].ports['o1'].center[0] - 110), float(refs[9].ports['o1'].center[1])),
        ]
    )

    gf.routing.route_single(
        c,
        port1 = mzi_pack2.ports['o9'],
        port2 = refs[10].ports['o1'],
        cross_section = xs_sin,
    )
    gf.routing.route_single(
        c,
        port1 = mzi_pack2.ports['o8'],
        port2 = refs[11].ports['o1'],
        cross_section = xs_sin,
    )
    gf.routing.route_single(
        c,
        port1 = mzi_pack2.ports['o7'],
        port2 = refs[12].ports['o1'],
        cross_section = xs_sin,
    )
    gf.routing.route_single(
        c,
        port1 = mzi_pack2.ports['o6'],
        port2 = refs[13].ports['o1'],
        cross_section = xs_sin,
    )
    #---------------------------------------------------------------------------------------
    # MZIs Rib set
    #---------------------------------------------------------------------------------------
    mzi_pack4 = c.add_ref(MZIs_Pack4())
    # mzi_pack2.rotate(90)
    mzi_pack4.move((-1040, 850))

    gf.routing.route_single(
        c,
        port1 = mzi_pack4.ports['o1'],
        port2 = refs[14].ports['o1'],
        cross_section = xs_sin,
        waypoints = [
            (float(mzi_pack4.ports['o1'].center[0]) + 50, float(mzi_pack4.ports['o1'].center[1])),
            (float(mzi_pack4.ports['o1'].center[0]) + 50, float(die.ymax) - 350),
            (float(mzi_pack4.ports['o1'].center[0]) + 500, float(die.ymax) - 350),
            (float(mzi_pack4.ports['o1'].center[0]) + 500, float(die.ymax) - 450),
            (float(refs[14].ports['o1'].center[0]) -140, float(die.ymax) - 450),
            (float(refs[14].ports['o1'].center[0]) -140, float(refs[14].ports['o1'].center[1])),
        ]
    )
    gf.routing.route_single(
        c,
        port1 = mzi_pack4.ports['o6'],
        port2 = ecl2.ports['o3'],
        cross_section = xs_sin,
    )
    gf.routing.route_single(
        c,
        port1 = mzi_pack4.ports['o2'],
        port2 = mzi_pack2.ports['o5'],
        cross_section = 'strip',
        waypoints = [
            (float(mzi_pack4.ports['o2'].center[0]) + 70, float(mzi_pack4.ports['o2'].center[1])),
            (float(mzi_pack4.ports['o2'].center[0]) + 70, float(die.ymax) - 470),
            (float(mzi_pack2.ports['o5'].center[0]) + 30, float(die.ymax) - 470),
            (float(mzi_pack2.ports['o5'].center[0]) + 30, float(mzi_pack2.ports['o5'].center[1]) -30),
            (float(mzi_pack2.ports['o5'].center[0]) , float(mzi_pack2.ports['o5'].center[1]) -30),
        ]
    )

    gf.routing.route_single(
        c,
        port1 = mzi_pack4.ports['o3'],
        port2 = mzi_pack2.ports['o4'],
        cross_section = 'strip',
        waypoints = [
            (float(mzi_pack4.ports['o3'].center[0]) + 70, float(mzi_pack4.ports['o3'].center[1])),
            (float(mzi_pack4.ports['o3'].center[0]) + 70, float(die.ymax) - 480),
            (float(mzi_pack2.ports['o4'].center[0]) + 30, float(die.ymax) - 480),
            (float(mzi_pack2.ports['o4'].center[0]) + 30, float(mzi_pack2.ports['o4'].center[1]) -30),
            (float(mzi_pack2.ports['o4'].center[0]) , float(mzi_pack2.ports['o4'].center[1]) -30),
        ]
    )

    gf.routing.route_single(
        c,
        port1 = mzi_pack4.ports['o4'],
        port2 = mzi_pack2.ports['o3'],
        cross_section = 'strip',
        waypoints = [
            (float(mzi_pack4.ports['o4'].center[0]) + 235, float(mzi_pack4.ports['o4'].center[1])),
            (float(mzi_pack4.ports['o4'].center[0]) + 235, float(mzi_pack4.ports['o5'].center[1]) + 15),
            (float(mzi_pack4.ports['o3'].center[0]) + 80, float(mzi_pack4.ports['o5'].center[1]) + 15),

            
            (float(mzi_pack4.ports['o3'].center[0]) + 80, float(die.ymax) - 490),
            (float(mzi_pack2.ports['o3'].center[0]) + 30, float(die.ymax) - 490),
            (float(mzi_pack2.ports['o3'].center[0]) + 30, float(mzi_pack2.ports['o3'].center[1]) -30),
            (float(mzi_pack2.ports['o3'].center[0]) , float(mzi_pack2.ports['o3'].center[1]) -30),
        ]
    )

    gf.routing.route_single(
        c,
        port1 = mzi_pack4.ports['o5'],
        port2 = mzi_pack2.ports['o2'],
        cross_section = 'strip',
        waypoints = [
            (float(mzi_pack4.ports['o3'].center[0]) + 90, float(mzi_pack4.ports['o5'].center[1])),
            (float(mzi_pack4.ports['o3'].center[0]) + 90, float(die.ymax) - 500),
            (float(mzi_pack2.ports['o2'].center[0]) + 30, float(die.ymax) - 500),
            (float(mzi_pack2.ports['o2'].center[0]) + 30, float(mzi_pack2.ports['o2'].center[1]) -30),
            (float(mzi_pack2.ports['o2'].center[0]) , float(mzi_pack2.ports['o2'].center[1]) -30),
        ]
    )
    
    #---------------------------------------------------------------------------------------
    # ECL to Wavementer
    #---------------------------------------------------------------------------------------
    ecl_wm_mmi = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    
    ecl_wm_mmi.xmax = wavemeter.xmin - 20
    ecl_wm_mmi.ymax = wavemeter.ports['o1'].center[1] - 20

    gf.routing.route_single(
        c,
        port1 = ecl_wm_mmi.ports['o2'],
        port2 = wavemeter.ports['o1'],
        cross_section = 'strip',
    )

    gf.routing.route_single(
        c,
        port1 = ecl2wl.ports['o5'],
        port2 = ecl_wm_mmi.ports['o1'],
        cross_section = 'strip',
        waypoints = [
            (float(ecl2wl.ports['o5'].center[0] + 20), float(ecl2wl.ports['o5'].center[1])),
            (float(ecl2wl.ports['o5'].center[0] + 20), float(ecl2wl.ports['o5'].center[1] + 40)),
            (float(ecl2.ports['o3'].center[0] + 15), float(ecl2wl.ports['o5'].center[1] + 40)),
            (float(ecl2.ports['o3'].center[0] + 15), float(ecl_wm_mmi.ports['o1'].center[1] )),
        ],
    )

    external_wl_via = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    external_wl_via.mirror_x()
    external_wl_via.xmax = ecl2wl.ports['o6'].center[0] - 100
    external_wl_via.ymin = ecl2wl.ports['o6'].center[1] + 50
    gf.routing.route_single(
        c,
        port1 = ecl2wl.ports['o6'],
        port2 = external_wl_via.ports['o1'],
        cross_section = 'strip',
    )

    gf.routing.route_single(
        c,
        port1 = external_wl_via.ports['o2'],
        port2 = refs[3].ports['o1'],
        cross_section = xs_sin,
        waypoints = [
            (float(ecl2wl.ports['o5'].center[0] + 5), float(external_wl_via.ports['o2'].center[1])),
            (float(ecl2wl.ports['o5'].center[0] + 5), float(bpads[0].ports['e3'].center[1] + 10)),
            (float(refs[3].ports['o1'].center[0] - 55), float(bpads[0].ports['e3'].center[1] + 10)),
            (float(refs[3].ports['o1'].center[0] - 55), float(refs[3].ports['o1'].center[1])),
        ]
    )

    #------- ECL-Wavemeter-out
    via_ecl_wm = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via_ecl_wm.xmin = ecl_wm_mmi.xmax + 100
    via_ecl_wm.y = ecl_wm_mmi.y - 120

    gf.routing.route_single(
        c,
        port1 = ecl_wm_mmi.ports['o3'],
        port2 = wavemeter.ports['o2'],
        cross_section = 'strip',
    )
    gf.routing.route_single(
        c,
        port1 = wavemeter.ports['o3'],
        port2 = via_ecl_wm.ports['o1'],
        cross_section = 'strip',
    )
    gf.routing.route_single(
        c,
        port1 = via_ecl_wm.ports['o2'],
        port2 = refs[15].ports['o1'],
        cross_section = xs_sin,
        waypoints = [
            (float(refs[15].ports['o1'].center[0]) -130, via_ecl_wm.ports['o2'].center[1]),
            (float(refs[15].ports['o1'].center[0]) -130, float(refs[15].ports['o1'].center[1])),
        ]
    )

    
    #---------------------------------------------------------------------------------------
    # Shahab bulshit
    #---------------------------------------------------------------------------------------
    current_mirror = c.add_ref(gf.import_gds("/workspace/myamf/gds/CurrentMirror_5.gds"))
    current_mirror.move((-4100, 20))

    #---------------------------------------------------------------------------------------
    # Logo
    #---------------------------------------------------------------------------------------
    logo_gds = gf.import_gds("/workspace/myamf/gds/quiet_logo.gds")
    logo_gds.remap_layers({(1, 0): (125, 0)})  # move to Metal 2 layer
    logo = c.add_ref(logo_gds)
    # logo.xmax =  250
    # logo.ymax = die.ymax - 1400
    logo.move((-420, 300))


    return c
