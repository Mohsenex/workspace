import gdsfactory as gf
from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_Si2X2MMI_Cband_v5p0,
    AMF_300LSOI_SiVOA_Cband_v5p0,
)
from .Phase_Shifter import Phase_Shifter
from .Tunable_Coupler import Tunable_Coupler
from gdsfactory.pdk import get_active_pdk

@gf.cell
def ECL_to_WL()->gf.Component:
    c = gf.Component()
    
    tc1 = c.add_ref(Tunable_Coupler())
   

    ps = c.add_ref(Phase_Shifter())
    ps.xmin = tc1.ports['o4'].center[0] + 10
    ps.movey(tc1.ports['o4'].center[1])

    tc2 = c.add_ref(Tunable_Coupler())
    tc2.xmin = ps.xmax + 10
   
    #---------------------------------------------------------------------------------------
    # PADs — 38 individual pads, 125 µm pitch, centered at top of die
    #---------------------------------------------------------------------------------------
    # pdk = get_active_pdk()

    # N_PADS = 7
    # PAD_PITCH = 125.0
    # pad_cell = pdk.get_component("pad")

    # pads = []
    # x_start = 100 
    # for i in range(N_PADS):
    #     p = c.add_ref(pad_cell)
    #     p.x = x_start + i * PAD_PITCH
    #     p.ymax = voa.ymin - 80
    #     pads.append(p)

    #----------------------------------------------
    # Optical Routing
    #----------------------------------------------
    gf.routing.route_single(
        c,
        port1 = tc1.ports['o4'],
        port2 = ps.ports['o1'],
        cross_section = 'strip',
    )

    gf.routing.route_single(
        c,
        port1 = ps.ports['o2'],
        port2 = tc2.ports['o1'],
        cross_section = 'strip',
    )

    #----------------------------------------------
    # Electrical Routing
    #----------------------------------------------
    # gf.routing.route_bundle(
    #     c,
    #     ports1 = [ps.ports['e1'], ps.ports['e2']],
    #     ports2= [pads[0].ports['e2'], pads[1].ports['e2']],
    #     cross_section = "metal_routing",
    # )

    # gf.routing.route_bundle(
    #     c,
    #     ports1 = [voa.ports['e3'], voa.ports['e2'], voa.ports['e1']],
    #     ports2= [pads[2].ports['e2'], pads[3].ports['e2'], pads[4].ports['e2']],
    #     cross_section = "metal_routing",
    # )

    # gf.routing.route_bundle(
    #     c,
    #     ports1 = [tc.ports['e1'], tc.ports['e2']],
    #     ports2= [pads[5].ports['e2'], pads[6].ports['e2']],
    #     cross_section = "metal_routing",
    # )

    #----------------------------------------------
    # Add Ports
    #----------------------------------------------
    c.add_port('o1', port = tc1.ports['o1'])
    c.add_port('o2', port = tc1.ports['o2'])
    c.add_port('o3', port = tc2.ports['o3'])
    c.add_port('o4', port = tc2.ports['o4'])

    c.add_port('e1', port = tc1.ports['e1'])
    c.add_port('e2', port = tc1.ports['e2'])
    c.add_port('e3', port = ps.ports['e1'])
    c.add_port('e4', port = ps.ports['e2'])
    c.add_port('e5', port = tc2.ports['e1'])
    c.add_port('e6', port = tc2.ports['e2'])
   
    return c
