import gdsfactory as gf
from gdsfactory.pdk import get_active_pdk

from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_LSiN2SOISSC_Cband_v5p0,
    AMF_300LSOI_PowMonitor_Cband_Cell_v5p0)
from amf.config import PATH
from amf.chp.tech import LAYER, TECH
from amf.import_gds import import_gds


from .Balanced_PD import Balanced_PD


gdsdir = PATH.gds_chp

N_FIBERS = 22
PITCH = 127.0  # um
DIE_SIZE = (7400, 3000)


@gf.cell
def ECL1() -> gf.Component:
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

   

    #---------------------------------------------------------------------------------------
    # ECL1 
    #---------------------------------------------------------------------------------------

    ecl1 = gf.import_gds("/workspace/myamf/gds/FonexQuietXECL_InsideOut_Hybrid_V2026_3.gds", skip_new_cells=True)
    # SiN Ports:
    ecl1.add_port(name="o1", center=(416.054, 209.414), width=1.0, orientation=0, layer='WG_SIN')
   
    # Si Ports:
    ecl1.add_port(name="o2", center=(-452.946, -81.658), width=0.5, orientation=270, layer='WG')
    ecl1.add_port(name="o3", center=(864.054, -171.658), width=0.5, orientation=0, layer='WG')
    ecl1.add_port(name="o4", center=(864.054, -170.324), width=0.5, orientation=0, layer='WG')
    ecl1.add_port(name="o5", center=(503.36, 490.21), width=0.5, orientation=90, layer='WG')
    ecl1.add_port(name="o6", center=(-599.84, 390.466), width=0.5, orientation=180, layer='WG')
    ecl1.add_port(name="o7", center=(-599.84, 538.62), width=0.5, orientation=180, layer='WG')
   
    # Metal 2 Ports:
    ecl1.add_port(name="e1", center=(-322.306, -9.305), width=20, orientation=90,  layer="MT2", port_type="electrical")
    ecl1.add_port(name="e2", center=(-235.616, -26.705), width=20, orientation=90,  layer="MT2", port_type="electrical")
    # ecl1.add_port(name="e3", center=(-322.306, -17.557), width=20, orientation=90,  layer="MT2", port_type="electrical")
    # ecl1.add_port(name="e4", center=(-235.616, -34.957), width=20, orientation=90,  layer="MT2", port_type="electrical")
    ecl1.add_port(name="e5", center=(-390.170, 620.874), width=20, orientation=90,  layer="MT2", port_type="electrical")
    ecl1.add_port(name="e6", center=(-318.68, 620.874), width=20, orientation=90,  layer="MT2", port_type="electrical")
    ecl1.add_port(name="e7", center=(-239.98, 621.256), width=20, orientation=90,  layer="MT2", port_type="electrical")
    ecl1.add_port(name="e8", center=(-167.73, 620.874), width=20, orientation=90,  layer="MT2", port_type="electrical")
    ecl1.add_port(name="e9", center=(286, 511.232), width=20, orientation=90,  layer="MT2", port_type="electrical")
    ecl1.add_port(name="e10", center=(372.69, 493.832), width=20, orientation=90,  layer="MT2", port_type="electrical")
    # ecl1.add_port(name="e11", center=(286, 449.823), width=20, orientation=90,  layer="MT2", port_type="electrical")
    # ecl1.add_port(name="e12", center=(372.69, 419.283), width=20, orientation=90,  layer="MT2", port_type="electrical")
    ecl1.add_port(name="e13", center=(118.359, 327.934), width=20, orientation=90,  layer="MT2", port_type="electrical")
    ecl1.add_port(name="e14", center=(458.359, 346.114), width=20, orientation=90,  layer="MT2", port_type="electrical")
    ecl1.add_port(name="e15", center=(606.054, -169.658), width=20, orientation=270,  layer="MT2", port_type="electrical")
    ecl1.add_port(name="e16", center=(718.554, -187.658), width=20, orientation=270,  layer="MT2", port_type="electrical")
    ecl1.add_port(name="e17", center=(249.66, -138.869), width=20, orientation=270,  layer="MT2", port_type="electrical")
    ecl1.add_port(name="e18", center=(183.43, -138.179), width=20, orientation=270,  layer="MT2", port_type="electrical")

    ecl1 = c.add_ref(ecl1)
    ecl1.xmin = die.xmin - 6
    ecl1.movey(600)

    #----------Metal Routing ---------------------
    gf.routing.route_single(
        c,
        port1 = ecl1.ports['e2'],
        port2 = pads[3].ports['e4'],
        cross_section = 'metal_routing',
        waypoints = [
            (float(ecl1.ports['e2'].center[0]) , float(ecl1.ports['e2'].center[1]) + 100),
            (float(ecl1.ports['e2'].center[0]) - 250 , float(ecl1.ports['e2'].center[1]) + 100),
            (float(ecl1.ports['e2'].center[0]) - 250 , float(pads[3].ports['e4'].center[1]) - 50),
            (float(pads[3].ports['e4'].center[0]) , float(pads[3].ports['e4'].center[1]) -50),
        ],
    )
    gf.routing.route_single(
        c,
        port1 = ecl1.ports['e1'],
        port2 = pads[2].ports['e4'],
        cross_section = 'metal_routing',
        waypoints = [
            (float(ecl1.ports['e1'].center[0]) , float(ecl1.ports['e1'].center[1]) + 60),
            (float(ecl1.ports['e1'].center[0]) - 180 , float(ecl1.ports['e1'].center[1]) + 60),
            (float(ecl1.ports['e1'].center[0]) - 180 , float(pads[2].ports['e4'].center[1]) - 30),
            (float(pads[2].ports['e4'].center[0]) , float(pads[2].ports['e4'].center[1]) -30),
        ],
    )


    gf.routing.route_bundle(
        c,
        ports1 = [ecl1.ports['e5'], ecl1.ports['e6'], ecl1.ports['e7'], ecl1.ports['e8']],
        ports2 = [pads[4].ports['e4'], pads[5].ports['e4'], pads[6].ports['e4'], pads[7].ports['e4']],
        cross_section = 'metal_routing',
    )

    gf.routing.route_single(
        c,
        port1 = ecl1.ports['e9'],
        port2 = pads[9].ports['e4'],
        cross_section = 'metal_routing',
        waypoints= [
            (float(ecl1.ports['e9'].center[0]), float(ecl1.ports['e9'].center[1]) + 70),
            (float(pads[9].ports['e4'].center[0]), float(ecl1.ports['e9'].center[1]) + 70),
        ]
    )

    gf.routing.route_single(
        c,
        port1 = ecl1.ports['e10'],
        port2 = pads[10].ports['e4'],
        cross_section = 'metal_routing',
        waypoints = [
            (float(ecl1.ports['e10'].center[0]), float(ecl1.ports['e9'].center[1]) + 50),
            (float(pads[10].ports['e4'].center[0]), float(ecl1.ports['e9'].center[1]) + 50),
        ],
    )

    gf.routing.route_single(
        c,
        port1 = ecl1.ports['e13'],
        port2 = pads[8].ports['e4'],
        cross_section = 'metal_routing',
        waypoints = [
            (float(ecl1.ports['e13'].center[0]), float(ecl1.ports['e9'].center[1]) + 90),
            (float(pads[8].ports['e4'].center[0]), float(ecl1.ports['e9'].center[1]) + 90),
        ],
    )
    gf.routing.route_single(
        c,
        port1 = ecl1.ports['e14'],
        port2 = pads[10].ports['e4'],
        cross_section = 'metal_routing',
    )

    gf.routing.route_single(
        c,
        port1 = ecl1.ports['e16'],
        port2 = pads[10].ports['e4'],
        cross_section = 'metal_routing',
        waypoints = [
            (float(ecl1.ports['e16'].center[0]), float(ecl1.ports['e16'].center[1]) - 20),
            (float(ecl1.ports['e16'].center[0] + 160), float(ecl1.ports['e16'].center[1]) - 20),
            (float(ecl1.ports['e16'].center[0] + 160), float(ecl1.ports['e16'].center[1]) + 160),
            (float(pads[10].ports['e4'].center[0]), float(ecl1.ports['e16'].center[1]) + 160),
        ],
    )
    gf.routing.route_single(
        c,
        port1 = ecl1.ports['e15'],
        port2 = pads[11].ports['e4'],
        cross_section = 'metal_routing',
        waypoints = [
            (float(ecl1.ports['e15'].center[0]), float(ecl1.ports['e16'].center[1]) - 35),
            (float(ecl1.ports['e15'].center[0] + 290), float(ecl1.ports['e16'].center[1]) - 35),
            (float(ecl1.ports['e15'].center[0] + 290), float(ecl1.ports['e16'].center[1]) + 180),
            (float(pads[11].ports['e4'].center[0]), float(ecl1.ports['e16'].center[1]) + 180),
        ],
    )
    gf.routing.route_single(
        c,
        port1 = ecl1.ports['e17'],
        port2 = pads[12].ports['e4'],
        cross_section = 'metal_routing',
        waypoints = [
            (float(ecl1.ports['e17'].center[0]), float(ecl1.ports['e16'].center[1]) - 50),
            (float(ecl1.ports['e15'].center[0] + 305), float(ecl1.ports['e16'].center[1]) - 50),
            (float(ecl1.ports['e15'].center[0] + 305), float(ecl1.ports['e16'].center[1]) + 195),
            (float(pads[12].ports['e4'].center[0]), float(ecl1.ports['e16'].center[1]) + 195),
        ],
    )
    gf.routing.route_single(
        c,
        port1 = ecl1.ports['e18'],
        port2 = pads[13].ports['e4'],
        cross_section = 'metal_routing',
        waypoints = [
            (float(ecl1.ports['e18'].center[0]), float(ecl1.ports['e16'].center[1]) - 65),           
            (float(pads[13].ports['e4'].center[0]), float(ecl1.ports['e16'].center[1]) - 65),
        ],
    )
    
    #--------------------- PD and Balanced PD--------------------
    pd1 = c.add_ref(AMF_300LSOI_PowMonitor_Cband_Cell_v5p0())
    pd1.rotate(90)
    pd1 .xmin = pads[0].ports['e3'].center[0]
    pd1.ymax = pads[14].ports['e4'].center[1] - 80
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

    pd2 = c.add_ref(AMF_300LSOI_PowMonitor_Cband_Cell_v5p0())
    pd2.rotate(90)
    pd2 .xmin = pads[14].ports['e3'].center[0]
    pd2.ymax = pads[14].ports['e4'].center[1] - 60

    via_pd2_e1 = c.add_ref(pdk.get_component("via_stack_m1_m2"))
    via_pd2_e2 = c.add_ref(pdk.get_component("via_stack_m1_m2"))
    via_pd2_e1.x = float(pads[14].ports['e4'].center[0])
    via_pd2_e1.y = float(pd2.ports['e1'].center[1]  + 40)
    via_pd2_e2.x = float(pads[15].ports['e4'].center[0])
    via_pd2_e2.y = float(pd2.ports['e2'].center[1] +40)

    gf.routing.route_bundle(
        c,
        ports1=[pd2.ports['e1'], pd2.ports['e2']],
        ports2=[via_pd2_e1.ports['e3'], via_pd2_e2.ports['e1']],
        cross_section='metal1',
        auto_taper=False,
        allow_layer_mismatch=True,
        allow_width_mismatch=True,
    )
    gf.routing.route_single(
        c,
        port1=via_pd2_e1.ports['e2'],
        port2=pads[14].ports['e4'],
        cross_section='metal_routing',
    )
    gf.routing.route_single(
        c,
        port1=via_pd2_e2.ports['e2'],
        port2=pads[15].ports['e4'],
        cross_section='metal_routing',
    )

    bpd = c.add_ref(Balanced_PD())
    bpd.xmin = pads[16].ports['e1'].center[0]
    bpd.ymax = pads[16].ports['e2'].center[1]


    #------------- Si Routing ----------------
    gf.routing.route_single(
        c,
        port1 = ecl1.ports['o3'],
        port2 = bpd.ports['o2'],
        cross_section = 'strip',
        waypoints = [
            (float(ecl1.ports['o3'].center[0]) + 20, float(ecl1.ports['o3'].center[1])),
            (float(ecl1.ports['o3'].center[0]) + 20, float(pd2.ports['o1'].center[1]) - 25),
            (float(bpd.ports['o2'].center[0]), float(pd2.ports['o1'].center[1]) - 25),
        ]
    )
    gf.routing.route_single(
        c,
        port1 = ecl1.ports['o4'],
        port2 = bpd.ports['o1'],
        cross_section = 'strip',
        waypoints = [
            (float(ecl1.ports['o4'].center[0]) + 15, float(ecl1.ports['o4'].center[1])),
            (float(ecl1.ports['o4'].center[0]) + 15, float(pd2.ports['o1'].center[1]) - 20),
            (float(bpd.ports['o1'].center[0]), float(pd2.ports['o1'].center[1]) - 20),
        ]
    )

    gf.routing.route_single(
        c,
        port1 = ecl1.ports['o2'],
        port2 = pd1.ports['o1'],
        cross_section = 'strip',
        waypoints = [
            (float(ecl1.ports['o2'].center[0]), float(ecl1.ports['o2'].center[1])-20),
            (float(ecl1.ports['o6'].center[0]) + 15, float(ecl1.ports['o2'].center[1]) -20),
            (float(ecl1.ports['o6'].center[0]) + 15, float(ecl1.ports['o2'].center[1]) + 100 ),
            (float(ecl1.ports['o6'].center[0]) - 40, float(ecl1.ports['o2'].center[1]) + 100 ),
            # (float(ecl1.ports['o6'].center[0]) - 40, float(ecl1.ports['o2'].center[1]) -20),
            (float(ecl1.ports['o6'].center[0]) - 40, float(pd1.ports['o1'].center[1]) -15),
            (float(pd1.ports['o1'].center[0]), float(pd1.ports['o1'].center[1]) -15),
        ]
    )

    #------------- Tap Coupler ----------------------
    tap= gf.Path()
    tap += gf.path.arc(radius=20, angle=180)    
    tap = tap.extrude('strip')
    tap = c.add_ref(tap)
    tap.rotate(-90)
    tap.move((-2225, 565.336))

    term = c.add_ref(gf.components.terminator(doping_layers=[]))
    term.rotate(90)
    term.connect('o1', tap.ports['o1'])

    gf.routing.route_single(
        c,
        port1 = tap.ports['o2'],
        port2 = pd2.ports['o1'],
        cross_section = 'strip',
        waypoints = [
            (float(tap.ports['o2'].center[0]), float(tap.ports['o2'].center[1]) + 20),
            (float(ecl1.ports['o4'].center[0]) + 10, float(tap.ports['o2'].center[1]) + 20),
            (float(ecl1.ports['o4'].center[0]) + 10, float(pd2.ports['o1'].center[1]) -15),
            (float(pd2.ports['o1'].center[0]), float(pd2.ports['o1'].center[1]) -15),
        ]
    )

    #---------- Vias ---------------------------------
    #---------- Vias ---------------------------------
    # ssc_gds = gdsdir / "AMF_300LSOI_LSiN2SOISSC_Cband_v5p0.gds"
    # ssc_comp = import_gds(ssc_gds)
    # ssc_comp.add_port(name="o1", center=(0.0, 0.0), width=0.5, orientation=180, layer='RIB')
    # ssc_comp.add_port(name="o2", center=(121.0, 0.0), width=1.0, orientation=0, layer='WG_SIN')

    via1 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via1.rotate(90)
    via1.xmin = ecl1.ports['o7'].center[0] + 40
    via1.ymin = ecl1.ports['o7'].center[1] + 40

    via2 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via2.rotate(90)
    via2.xmin = ecl1.ports['o7'].center[0] + 50
    via2.ymin = ecl1.ports['o7'].center[1] + 40

    via3 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via3.rotate(90)
    via3.x = ecl1.ports['o5'].center[0] 
    via3.ymin = ecl1.ports['o5'].center[1] + 90

    gf.routing.route_single(
        c,
        port1=ecl1.ports['o7'],
        port2=via2.ports['o1'],
        cross_section='strip',
        waypoints =[
            (float(ecl1.ports['o7'].center[0]) - 15, float(ecl1.ports['o7'].center[1])),
            (float(ecl1.ports['o7'].center[0]) - 15, float(ecl1.ports['o7'].center[1]) + 20),
            (float(via2.ports['o1'].center[0]), float(ecl1.ports['o7'].center[1]) + 20),
        ]
    )

    gf.routing.route_single(
        c,
        port1=ecl1.ports['o6'],
        port2=via1.ports['o1'],
        cross_section='strip',
        waypoints = [
            (float(ecl1.ports['o6'].center[0]) - 20, float(ecl1.ports['o6'].center[1])),
            (float(ecl1.ports['o6'].center[0]) - 20, float(ecl1.ports['o7'].center[1]) + 25),
            (float(via1.ports['o1'].center[0]), float(ecl1.ports['o7'].center[1]) + 25),
        ]
    )

    gf.routing.route_single(
        c,
        port1=ecl1.ports['o5'],
        port2=via3.ports['o1'],
        cross_section='strip',
    )

    #-------------- Adding Ports---------------------
    c.add_port('o1', port = ecl1.ports['o1'])
    c.add_port('o2', port = via3.ports['o2'])
    c.add_port('o3', port = via2.ports['o2'])
    c.add_port('o4', port = via1.ports['o2'])

    return c

    