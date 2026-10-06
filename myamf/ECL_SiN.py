import gdsfactory as gf
from .Ring_SiN import *
from .EC_SiN import *
from .MMI_Placeholder import *
from .Tunable_Coupler_SiN import *
import numpy as np
from amf.chp.cells.fixed import (
    AMF_300LSOI_Si2X2MMI_Cband_v5p0,)


@gf.cell(check_instances=False)
def ECL_SiN(
    #----- Edge coupler parameters--------
    ec_length: float = 150,
    ec_tip: float = 0.3,
    ec_end_width: float = 1,
    ec_constant_length: float = 50,
    ec_angle: float = 15,
    #------ Ring 1 parameters-------------
    R1_gap1=0.3, 
    R1_gap2 =0.3, 
    R1_radius =240, 
    R1_wg_width = 1, 
    R1_heater = True, 
    R1_heater_width = 5, 
    R1_heater_angle = 120,
    #------ Ring 2 parameters-------------
    R2_gap1=0.3, 
    R2_gap2 =0.3, 
    R2_radius =236, 
    R2_wg_width = 1, 
    R2_heater = True, 
    R2_heater_width = 5, 
    R2_heater_angle = 120,
    #------- Tunable copuler----------------
    tc_htr_length: float= 500,
    tc_htr_width: float= 5,
    tc_min_bending: float = 60,
    upper_htr = True,
    lower_htr = True,
    #------- Other parameters----------------
    ec_ring1_gap: float = 200,
    rings_gap = 200,
) -> gf.Component:
    c = gf.Component()

    xs_sin = gf.cross_section.strip(
        width=1,
        radius=60,
        radius_min=60,
        layer=LAYER.WG_SIN,
    )

    #---------- Edge Coupler --------------------------
    ec = c.add_ref(EC_SiN(
        ec_length=ec_length,
        ec_tip=ec_tip,
        ec_end_width=ec_end_width,
        ec_constant_length=ec_constant_length,
        ec_angle=ec_angle,
    ))

    #---------- Ring 1 --------------------------
    ring1 = c.add_ref(Ring_SiN(gap1=R1_gap1, gap2=R1_gap2, radius=R1_radius, wg_width=R1_wg_width, heater=R1_heater, heater_width=R1_heater_width, heater_angle=R1_heater_angle))
    ring1.rotate(90)
    ring1.move((ec.ports['o2'].center[0] + 2 * R1_radius + ec_ring1_gap, -R1_radius - (ec_length + ec_constant_length) * np.sin(ec_angle / 180 * np.pi)))

    #---------- Ring 2 --------------------------
    ring2 = c.add_ref(Ring_SiN(gap1=R2_gap1, gap2=R2_gap2, radius=R2_radius, wg_width=R2_wg_width, heater=R2_heater, heater_width=R2_heater_width, heater_angle=R2_heater_angle))
    ring2.rotate(-90)
    # Place ring2 so its o1 port is rings_gap to the right of ring1.o2, at the same y
    dx = ring1.ports['o2'].center[0] + rings_gap - ring2.ports['o1'].center[0]
    dy = ring1.ports['o2'].center[1] - ring2.ports['o1'].center[1]
    ring2.move((dx, dy))

    #---------- EC -> Ring1 route --------------------------
    gf.routing.route_single(
        c,
        port1=ec.ports['o2'],
        port2=ring1.ports['o4'],
        cross_section=xs_sin,
    )

    #---------- Ring1 -> Ring2 U-turn --------------------------
    arc = gf.Path()
    arc += gf.path.arc(radius=rings_gap / 2, angle=-180) 
    arc = c.add_ref(arc.extrude(xs_sin))
    arc.rotate(90)
    arc.connect('o1', ring1.ports['o2'])

    #---------- Tunable Coupler --------------------------

    arm = gf.Path()
    arm += gf.path.straight(length=R2_radius / 2 + 50 )
    arm += gf.path.arc(radius=150, angle=90)
    arm = c.add_ref(arm.extrude(xs_sin))
    arm.connect('o1', ring2.ports['o3'])

    tc = c.add_ref(Tunable_Coupler_SiN(htr_length = tc_htr_length, htr_width = tc_htr_width, min_bending = tc_min_bending, upper_htr = upper_htr, lower_htr = lower_htr))
    tc.connect('o3', arm.ports['o2'])

    gf.routing.route_single(
        c,
        port1 = tc.ports['o1'],
        port2 = tc.ports['o2'],
        cross_section = xs_sin,
    )

    
    return c
