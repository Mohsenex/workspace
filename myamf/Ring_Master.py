import gdsfactory as gf
import numpy as np
from gdsfactory.typings import CrossSectionSpec
import amf.chp as pdk
from amf.chp.tech import LAYER, TECH
from amf.chp.cells.fixed import (AMF_300LSOI_LSiN2SOISSC_Cband_v5p0)

@gf.cell
def Ring_Master(
    gap1: float =0.3,
    gap2: float =0.3,
    radius: float =120,
    wg_width: float = 1,
    heater = True,
    Si_SiN_Via = True,
    heater_width: float = 5,
    heater_angle: float = 120,
    cross_section='strip',
    layer = LAYER.WG_SIN
)->gf.Component:
    c = gf.Component()
    
    # ring = c << gf.get_component(
    #     "ring_single",
    #     gap=gap,
    #     radius=radius,
    #     # length_x=length_x,
    #     # length_y=length_y,
    #     cross_section=cross_section,
    # )
    ring = c.add_ref(gf.components.bend_circular(angle=360, radius = radius, width = wg_width, layer = layer, cross_section=cross_section, allow_min_radius_violation=False))
    bus_xs = gf.cross_section.cross_section(width=wg_width, layer=layer)
    bus1 = c.add_ref(gf.components.straight(length=radius, npoints=2, cross_section=bus_xs))
    bus1.move((-radius/2, - wg_width -gap1))
    bus2 = c.add_ref(gf.components.straight(length=radius, npoints=2, cross_section=bus_xs))
    bus2.move((-radius/2, 2*radius + wg_width +gap2))
    
    
    if heater:
        #--------- Heaters ---------------
        ht_xs = gf.cross_section.cross_section(width=heater_width, layer=LAYER.HTR)
        ht1_path = gf.path.arc(radius=radius, angle=heater_angle, npoints=720, start_angle= -heater_angle /2)
        ht1 = c.add_ref(gf.path.extrude(ht1_path, cross_section=ht_xs))
        ht2_path = gf.path.arc(radius=radius, angle=heater_angle, npoints=720, start_angle= -heater_angle /2 + 180)
        ht2 = c.add_ref(gf.path.extrude(ht2_path, cross_section=ht_xs))
        ht_patch_right_up = c.add_ref(gf.components.rectangle(size=(6, 6), layer=LAYER.HTR))
        ht_patch_right_up.move(( radius * np.cos(np.deg2rad(heater_angle /2)) - 3, radius + radius * np.sin(np.deg2rad(heater_angle /2)) - 3))
        ht_patch_right_down = c.add_ref(gf.components.rectangle(size=(6, 6), layer=LAYER.HTR))
        ht_patch_right_down.move(( radius * np.cos(np.deg2rad(heater_angle /2)) - 3, radius - radius * np.sin(np.deg2rad(heater_angle /2)) - 3))
        ht_patch_left_up = c.add_ref(gf.components.rectangle(size=(6, 6), layer=LAYER.HTR))
        ht_patch_left_up.move((- radius * np.cos(np.deg2rad(heater_angle /2)) - 3, radius + radius * np.sin(np.deg2rad(heater_angle /2)) - 3))
        ht_patch_left_down = c.add_ref(gf.components.rectangle(size=(6, 6), layer=LAYER.HTR))
        ht_patch_left_down.move((- radius * np.cos(np.deg2rad(heater_angle /2)) - 3, radius - radius * np.sin(np.deg2rad(heater_angle /2)) - 3))

        #-------- Metals ------------------
        mtl_xs = gf.cross_section.cross_section(width=heater_width + 2, layer=LAYER.MT2)
        mtl1_path = gf.path.arc(radius=radius, angle=180 - heater_angle , npoints=720, start_angle= -(180 - heater_angle) /2 - 90)
        mtl1 = c.add_ref(gf.path.extrude(mtl1_path, cross_section=mtl_xs))

        mtl_patch_right_up = c.add_ref(gf.components.compass(size=(10, 10), layer=LAYER.MT2, port_type="electrical", port_inclusion=0))
        mtl_patch_right_up.move((radius * np.cos(np.deg2rad(heater_angle /2)), radius + radius * np.sin(np.deg2rad(heater_angle /2))))
        mtl_patch_right_down = c.add_ref(gf.components.compass(size=(10, 10), layer=LAYER.MT2, port_type="electrical", port_inclusion=0))
        mtl_patch_right_down.move((radius * np.cos(np.deg2rad(heater_angle /2)), radius - radius * np.sin(np.deg2rad(heater_angle /2))))
        mtl_patch_left_up = c.add_ref(gf.components.compass(size=(10, 10), layer=LAYER.MT2, port_type="electrical", port_inclusion=0))
        mtl_patch_left_up.move((- radius * np.cos(np.deg2rad(heater_angle /2)), radius + radius * np.sin(np.deg2rad(heater_angle /2))))
        mtl_patch_left_down = c.add_ref(gf.components.compass(size=(10, 10), layer=LAYER.MT2, port_type="electrical", port_inclusion=0))
        mtl_patch_left_down.move((- radius * np.cos(np.deg2rad(heater_angle /2)), radius - radius * np.sin(np.deg2rad(heater_angle /2))))

        #-------- Vias -------------------
        via_right_down = c.add_ref(gf.components.compass(size=(3, 3), layer=LAYER.VIA2))
        via_right_down.move((radius * np.cos(np.deg2rad(heater_angle /2)), radius - radius * np.sin(np.deg2rad(heater_angle /2))))
        via_right_up = c.add_ref(gf.components.compass(size=(3, 3), layer=LAYER.VIA2))
        via_right_up.move((radius * np.cos(np.deg2rad(heater_angle /2)), radius + radius * np.sin(np.deg2rad(heater_angle /2))))
        via_left_up = c.add_ref(gf.components.compass(size=(3, 3), layer=LAYER.VIA2))
        via_left_up.move((-radius * np.cos(np.deg2rad(heater_angle /2)), radius + radius * np.sin(np.deg2rad(heater_angle /2))))
        via_left_down = c.add_ref(gf.components.compass(size=(3, 3), layer=LAYER.VIA2))
        via_left_down.move((-radius * np.cos(np.deg2rad(heater_angle /2)), radius - radius * np.sin(np.deg2rad(heater_angle /2))))

        #--------- Si-SiN Via----------------
    if Si_SiN_Via:
        via1 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
        via1.move((-121 -radius/2 , - wg_width -gap1))
        via2 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
        via2.mirror()
        via2.move((121 +radius/2 , - wg_width -gap1))

        via3 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
        via3.move((-121 -radius/2 , 2*radius + wg_width +gap2))
        via4 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
        via4.mirror()
        via4.move((121 +radius/2 , 2*radius + wg_width +gap2))

        #------------- Esposing ports to the parent component c
        c.add_port("via1_o1", port=via1.ports["o1"])  # Si side
        c.add_port("via2_o1", port=via2.ports["o1"])  # Si side
        c.add_port("via3_o1", port=via3.ports["o1"])  # Si side
        c.add_port("via4_o1", port=via4.ports["o1"])  # Si side

    c.draw_ports()
    return c
