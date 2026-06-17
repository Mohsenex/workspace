import gdsfactory as gf
from gdsfactory.pdk import get_active_pdk

from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_LSiN2SOISSC_Cband_v5p0)
from amf.config import PATH
from amf.import_gds import import_gds

from .Balanced_PD import Balanced_PD


gdsdir = PATH.gds_chp

N_FIBERS = 22
PITCH = 127.0
DIE_SIZE = (7500, 3100)


@gf.cell
def ECL3() -> gf.Component:
    c = gf.Component()
    pdk = get_active_pdk()

    die = c.add_ref(pdk.get_component("die_frame_full", size=DIE_SIZE))

    N_bPADS = 20
    bPAD_PITCH = 125.0
    pad_cell = pdk.get_component("pad")

    bpads = []
    x_start = die.xmin + 200
    for i in range(N_bPADS):
        p = c.add_ref(pad_cell)
        p.x = x_start + i * bPAD_PITCH
        p.ymin = die.ymin + 100
        bpads.append(p)

    #---------------------------------------------------------------------------------------
    # ECL3 GDS import + port definitions
    #---------------------------------------------------------------------------------------
    ecl3 = gf.import_gds("/workspace/myamf/gds/FonexQuietXECL_Hybrid_V2026_5.gds")
    # SiN Ports:
    ecl3.add_port(name="o1", center=(368.859, -31.721),  width=1.0, orientation=0,   layer='WG_SIN')
    ecl3.add_port(name="o2", center=(283.34,  211.579),  width=1.0, orientation=0,   layer='WG_SIN')
    # Si Ports:
    ecl3.add_port(name="o3", center=(-402.805, 335.119), width=0.5, orientation=180, layer='WG')
    ecl3.add_port(name="o4", center=(-402.805, 211.579), width=0.5, orientation=180, layer='WG')
    ecl3.add_port(name="o5", center=(447.808,  336.355), width=0.5, orientation=0,   layer='WG')
    # Metal 2 Ports:
    ecl3.add_port(name="e1",  center=(-390.103,  104.699), width=20, orientation=270, layer="MT2", port_type="electrical")
    ecl3.add_port(name="e2",  center=(-319.813,  104.699), width=20, orientation=270, layer="MT2", port_type="electrical")
    ecl3.add_port(name="e3",  center=(-239.933,  105.859), width=20, orientation=270, layer="MT2", port_type="electrical")
    ecl3.add_port(name="e4",  center=(-184.893,  104.699), width=20, orientation=270, layer="MT2", port_type="electrical")
    ecl3.add_port(name="e5",  center=( 135.04, -119.885), width=20, orientation=270, layer="MT2", port_type="electrical")
    ecl3.add_port(name="e6",  center=( 202.81, -119.955), width=20, orientation=270, layer="MT2", port_type="electrical")
    ecl3.add_port(name="e7",  center=( 468.828,  108.585), width=20, orientation=0,  layer="MT2", port_type="electrical")
    ecl3.add_port(name="e8",  center=( 451.428,  209.815), width=20, orientation=0,  layer="MT2", port_type="electrical")
    ecl3.add_port(name="e9",  center=( 247.859,  353.055), width=20, orientation=90, layer="MT2", port_type="electrical")
    ecl3.add_port(name="e10", center=(-92.141,  415.645), width=20, orientation=90, layer="MT2", port_type="electrical")

    ecl3 = c.add_ref(ecl3)
    ecl3.xmin = die.xmin + 44
    ecl3.ymin = die.ymin + 400

    #---------------------------------------------------------------------------------------
    # Electrical Routing
    #---------------------------------------------------------------------------------------
    gf.routing.route_bundle(
        c,
        ports1=[ecl3.ports['e1'], ecl3.ports['e2'], ecl3.ports['e3'], ecl3.ports['e4']],
        ports2=[bpads[0].ports['e2'], bpads[1].ports['e2'], bpads[2].ports['e2'], bpads[3].ports['e2']],
        cross_section="metal_routing",
    )
    gf.routing.route_bundle(
        c,
        ports1=[ecl3.ports['e5'], ecl3.ports['e6']],
        ports2=[bpads[4].ports['e2'], bpads[5].ports['e2']],
        cross_section="metal_routing",
    )
    gf.routing.route_single(
        c,
        port1=ecl3.ports['e7'],
        port2=bpads[6].ports['e2'],
        cross_section="metal_routing",
        waypoints=[
            (float(ecl3.ports['e7'].center[0] + 20), float(ecl3.ports['e7'].center[1])),
            (float(ecl3.ports['e7'].center[0] + 20), float(ecl3.ports['e7'].center[1] - 275)),
            (float(bpads[6].ports['e2'].center[0]),  float(ecl3.ports['e7'].center[1] - 275)),
        ],
    )
    gf.routing.route_single(
        c,
        port1=ecl3.ports['e8'],
        port2=bpads[7].ports['e2'],
        cross_section="metal_routing",
        waypoints=[
            (float(ecl3.ports['e8'].center[0] + 60), float(ecl3.ports['e8'].center[1])),
            (float(ecl3.ports['e8'].center[0] + 60), float(ecl3.ports['e7'].center[1] - 295)),
            (float(bpads[7].ports['e2'].center[0]),  float(ecl3.ports['e7'].center[1] - 295)),
        ],
    )
    gf.routing.route_single(
        c,
        port1=ecl3.ports['e9'],
        port2=bpads[7].ports['e2'],
        cross_section="metal_routing",
        waypoints=[
            (float(ecl3.ports['e9'].center[0]),      float(ecl3.ports['e9'].center[1] + 20)),
            (float(ecl3.ports['e8'].center[0] + 60), float(ecl3.ports['e9'].center[1] + 20)),
            (float(ecl3.ports['e8'].center[0] + 60), float(ecl3.ports['e7'].center[1] - 295)),
            (float(bpads[7].ports['e2'].center[0]),  float(ecl3.ports['e7'].center[1] - 295)),
        ],
    )
    gf.routing.route_single(
        c,
        port1=ecl3.ports['e10'],
        port2=bpads[8].ports['e2'],
        cross_section="metal_routing",
        waypoints=[
            (float(ecl3.ports['e10'].center[0]),     float(ecl3.ports['e10'].center[1] + 20)),
            (float(ecl3.ports['e8'].center[0] + 80), float(ecl3.ports['e10'].center[1] + 20)),
            (float(ecl3.ports['e8'].center[0] + 80), float(ecl3.ports['e7'].center[1] - 310)),
            (float(bpads[8].ports['e2'].center[0]),  float(ecl3.ports['e7'].center[1] - 310)),
        ],
    )

    #---------------------------------------------------------------------------------------
    # Balanced PDs
    #---------------------------------------------------------------------------------------
    bpd12 = c.add_ref(Balanced_PD())
    bpd12.mirror_y()
    bpd12.ymin = bpads[9].ports['e4'].center[1]
    bpd12.xmin = bpads[9].ports['e1'].center[0]

    bpd34 = c.add_ref(Balanced_PD())
    bpd34.mirror_y()
    bpd34.ymin = bpads[12].ports['e4'].center[1]
    bpd34.xmin = bpads[12].ports['e1'].center[0]

    #---------------------------------------------------------------------------------------
    # SiN→Si vias
    # SSC cell: o1 (Si) at local x=0, o2 (SiN) at local x=121. After mirror_x the SiN
    # port (o2) ends up at xmin of the placed ref. We position vias by xmin and movey.
    #---------------------------------------------------------------------------------------
    via3_xmin = ecl3.xmax + 80
    via3_y    = ecl3.ports['o1'].center[1]
    via4_y    = ecl3.ports['o2'].center[1]
    # SSC o1 (Si output after mirror_x) is at the right edge: xmin + 121
    via3_o1_x = via3_xmin + 121
    via4_o1_x = via3_xmin + 121  # same xmin

    via3 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via3.mirror_x()
    via3.xmin = via3_xmin
    via3.movey(via3_y)

    via4 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via4.mirror_x()
    via4.xmin = via3_xmin
    via4.movey(via4_y)

    #---------------------------------------------------------------------------------------
    # 1×2 MMI splitters
    # MMI o1 is at local x=0 (west input), o2/o3 at x=55 (east outputs).
    # mmi3/mmi4 are snapped to via3/via4 Si output ports using computed positions.
    #---------------------------------------------------------------------------------------
    mmi1 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    mmi1.xmin = ecl3.xmax - 150
    mmi1.ymin = ecl3.ymin - 35

    mmi2 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    mmi2.xmin = ecl3.xmax - 150
    mmi2.ymin = ecl3.ymin - 20

    # mmi3 input (o1 at x=0) snapped to via3 Si output
    mmi3 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    mmi3.move((via3_o1_x, via3_y))

    # mmi4 input snapped to via4 Si output
    mmi4 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    mmi4.move((via4_o1_x, via4_y))

    mmi5 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    mmi5.mirror_x()
    mmi5.xmin = via3_xmin
    mmi5.ymax = via3_y - 40

    #---------------------------------------------------------------------------------------
    # Si optical routing
    #---------------------------------------------------------------------------------------
    gf.routing.route_single(
        c,
        port1=ecl3.ports['o3'],
        port2=mmi1.ports['o1'],
        cross_section='strip',
        waypoints=[
            (float(ecl3.ports['o3'].center[0] - 30), float(ecl3.ports['o3'].center[1])),
            (float(ecl3.ports['o3'].center[0] - 30), float(mmi1.ports['o1'].center[1])),
        ],
    )
    gf.routing.route_single(
        c,
        port1=ecl3.ports['o4'],
        port2=mmi2.ports['o1'],
        cross_section='strip',
        waypoints=[
            (float(ecl3.ports['o4'].center[0] - 25), float(ecl3.ports['o4'].center[1])),
            (float(ecl3.ports['o4'].center[0] - 25), float(mmi2.ports['o1'].center[1])),
        ],
    )
    gf.routing.route_single(c, port1=mmi1.ports['o2'], port2=bpd12.ports['o1'], cross_section='strip')
    gf.routing.route_single(c, port1=mmi2.ports['o3'], port2=bpd12.ports['o2'], cross_section='strip')
    gf.routing.route_single(c, port1=mmi2.ports['o2'], port2=mmi5.ports['o3'], cross_section='strip')
    gf.routing.route_single(c, port1=mmi5.ports['o2'], port2=mmi3.ports['o3'], cross_section='strip')
    gf.routing.route_single(
        c,
        port1=mmi3.ports['o2'],
        port2=bpd34.ports['o1'],
        cross_section='strip',
        waypoints=[
            (float(mmi3.ports['o2'].center[0] + 15), float(mmi3.ports['o2'].center[1])),
            (float(mmi3.ports['o2'].center[0] + 15), float(bpd34.ports['o1'].center[1] + 10)),
            (float(bpd34.ports['o1'].center[0]),     float(bpd34.ports['o1'].center[1] + 10)),
        ],
    )
    gf.routing.route_single(
        c,
        port1=mmi4.ports['o3'],
        port2=bpd34.ports['o2'],
        cross_section='strip',
        waypoints=[
            (float(mmi4.ports['o3'].center[0] + 20), float(mmi4.ports['o3'].center[1])),
            (float(mmi4.ports['o3'].center[0] + 20), float(bpd34.ports['o2'].center[1] + 15)),
            (float(bpd34.ports['o2'].center[0]),      float(bpd34.ports['o2'].center[1] + 15)),
        ],
    )

    #---------------------------------------------------------------------------------------
    # SiN optical routing (ECL3 SiN ports → vias)
    # via o2 (SiN port, after mirror_x) is at xmin of the via ref, facing west (orientation=180).
    # We use add_port to expose a connectable port at the known position.
    #---------------------------------------------------------------------------------------
    # SSC after mirror_x: SiN port (o2) is at xmin of the ref, facing west (orientation=180).
    # We expose temporary ports on the component to give route_single connectable endpoints.
    via3_o2_center = (float(via3_xmin), float(via3_y))
    via4_o2_center = (float(via3_xmin), float(via4_y))

    c.add_port(name="_via3_sin", center=via3_o2_center, width=1.0, orientation=180, layer="WG_SIN")
    c.add_port(name="_via4_sin", center=via4_o2_center, width=1.0, orientation=180, layer="WG_SIN")

    gf.routing.route_single(c, port1=ecl3.ports['o1'], port2=c.ports['_via3_sin'], cross_section='nitride')
    gf.routing.route_single(c, port1=ecl3.ports['o2'], port2=c.ports['_via4_sin'], cross_section='nitride')

    #---------------------------------------------------------------------------------------
    # Expose ports
    #---------------------------------------------------------------------------------------
    c.add_port('o1', port=mmi1.ports['o3'])
    c.add_port('o2', port=mmi4.ports['o2'])
    c.add_port('o3', port=mmi5.ports['o1'])
    c.add_port('o4', port=ecl3.ports['o5'])

    return c


