import gdsfactory as gf
from .Ring_Master import Ring_Master
from amf.chp.tech import LAYER, TECH
from amf.chp.cells.fixed import (AMF_300LSOI_LSiN2SOISSC_Cband_v5p0,
AMF_300LSOI_SiGC1D_Cband_v5p0,
AMF_300LSOI_Si1X2MMI_Cband_v5p0,)

@gf.cell
def Rings_Pack()->gf.Component:
    c = gf.Component()
    ring_1000nm_with_heater = c.add_ref(Ring_Master(gap1=0.7, gap2=0.7, radius=120, wg_width = 1, heater = True, Si_SiN_Via = True, heater_width = 5, heater_angle = 120, cross_section='strip', layer = LAYER.WG_SIN))
    ring_1000nm_with_heater.rotate(90)
    ring_1000nm_without_heater = c.add_ref(Ring_Master(gap1=0.7, gap2=0.7, radius=120, wg_width = 1, heater = False, Si_SiN_Via = True, heater_width = 5, heater_angle = 120, cross_section='strip', layer = LAYER.WG_SIN))
    ring_1000nm_without_heater.rotate(90)
    ring_1000nm_without_heater.move((280, 0))
    ring_1250nm_with_heater = c.add_ref(Ring_Master(gap1=0.7, gap2=0.7, radius=130, wg_width = 1.25, heater = True, Si_SiN_Via = True, heater_width = 5, heater_angle = 120, cross_section='strip', layer = LAYER.WG_SIN))
    ring_1250nm_with_heater.rotate(90)
    ring_1250nm_with_heater.move((280 * 2 + 20, 0))
    ring_1250nm_without_heater = c.add_ref(Ring_Master(gap1=0.7, gap2=0.7, radius=130, wg_width = 1.25, heater = False, Si_SiN_Via = True, heater_width = 5, heater_angle = 120, cross_section='strip', layer = LAYER.WG_SIN))
    ring_1250nm_without_heater.rotate(90)
    ring_1250nm_without_heater.move((280 * 3 + 40, 0))

    # Array of 9 grating couplers, pitch = 127 um, rotated 90 degrees
    gcs = []
    for i in range(9):
        gc = c.add_ref(AMF_300LSOI_SiGC1D_Cband_v5p0())
        gc.mirror_x()
        gc.rotate(90)
        gc.move((-300  +i * 127, -250))
        gcs.append(gc)
    mmi1 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    mmi1.rotate(90)
    mmi1.move((-300  , -0))
    mmi2 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    mmi2.move((55 + 25, 25))
    mmi2.rotate(90)
    mmi2.move((-300  , 0))
    mmi3 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    mmi3.move((55 + 25, -25))
    mmi3.rotate(90)
    mmi3.move((-300 , 0))

    #------------- Routings----------------
    gf.routing.route_single(
        c,
        port1 = mmi1.ports['o3'],
        port2 = mmi3.ports['o1'],
        cross_section = 'strip',
    )

    gf.routing.route_single(
        c,
        port1 = mmi1.ports['o2'],
        port2 = mmi2.ports['o1'],
        cross_section = 'strip',
    )

    #----- Routing Inputs-----------
    gf.routing.route_single(
        c,
        port1 = gcs[0].ports['o1'],
        port2 = mmi1.ports['o1'],
        cross_section = 'strip',
    )
    gf.routing.route_single(
        c,
        port1 = mmi3.ports['o3'],
        port2 = ring_1000nm_with_heater.ports['via4_o1'],
        cross_section = 'strip',
    )

    gf.routing.route_single(
        c,
        port1 = mmi3.ports['o2'],
        port2 = ring_1000nm_without_heater.ports['via4_o1'],
        cross_section = 'strip',
        waypoints=[
            (mmi3.ports['o2'].center[0], ring_1000nm_without_heater.ports['via4_o1'].center[1]+ 35),
            (ring_1000nm_without_heater.ports['via4_o1'].center[0], ring_1000nm_without_heater.ports['via4_o1'].center[1]+ 35),
            ],
    )
    gf.routing.route_single(
        c,
        port1 = mmi2.ports['o3'],
        port2 = ring_1250nm_with_heater.ports['via4_o1'],
        cross_section = 'strip',
        waypoints=[
            (mmi2.ports['o3'].center[0], ring_1250nm_with_heater.ports['via4_o1'].center[1]+ 35),
            (ring_1250nm_with_heater.ports['via4_o1'].center[0], ring_1250nm_with_heater.ports['via4_o1'].center[1]+ 35),
            ],
    )
    gf.routing.route_single(
        c,
        port1 = mmi2.ports['o2'],
        port2 = ring_1250nm_without_heater.ports['via4_o1'],
        cross_section = 'strip',
        waypoints=[
            (mmi2.ports['o2'].center[0], ring_1250nm_without_heater.ports['via4_o1'].center[1]+ 40),
            (ring_1250nm_without_heater.ports['via4_o1'].center[0], ring_1250nm_without_heater.ports['via4_o1'].center[1]+ 40),
            ],
    )

    #-------------- Routing Outputs---------
    # Connect via2_o1 of each ring to gcs[1]-gcs[4]
    # gf.routing.route_bundle(
    #     c,
        
    return c
