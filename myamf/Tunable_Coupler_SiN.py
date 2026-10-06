import gdsfactory as gf
from .MMI_Placeholder import *
from amf.chp.tech import LAYER, TECH

@gf.cell
def Tunable_Coupler_SiN(
    htr_length: float = 500,
    htr_width: float = 5,
    min_bending: float = 60,
    upper_htr = True,
    lower_htr = True,
)->gf.Component:
    c = gf.Component()

    xs_sin = gf.cross_section.strip(
        width=1,
        radius=min_bending,
        radius_min= min_bending,
        layer=LAYER.WG_SIN,
    )

    mmi1 = c.add_ref(MMI_Placeholder())
    

    mmi2 = c.add_ref(MMI_Placeholder())
    mmi2.connect('o1', mmi1.ports['o3'])
    mmi2.movex(4 * min_bending + htr_length)

    gf.routing.route_single(
        c,
        port1 = mmi1.ports['o3'],
        port2 = mmi2.ports['o1'],
        cross_section = xs_sin,
        waypoints = [
            (float(mmi1.ports['o3'].center[0]) + min_bending, float(mmi1.ports['o3'].center[1])),
            (float(mmi1.ports['o3'].center[0]) + min_bending, float(mmi1.ports['o3'].center[1]) - 2*min_bending),
            (float(mmi2.ports['o1'].center[0]) - min_bending, float(mmi1.ports['o3'].center[1]) - 2*min_bending),
            (float(mmi2.ports['o1'].center[0]) - min_bending, float(mmi2.ports['o1'].center[1])),
        ]
    )

    gf.routing.route_single(
        c,
        port1 = mmi1.ports['o4'],
        port2 = mmi2.ports['o2'],
        cross_section = xs_sin,
        waypoints = [
            (float(mmi1.ports['o4'].center[0]) + min_bending, float(mmi1.ports['o4'].center[1])),
            (float(mmi1.ports['o4'].center[0]) + min_bending, float(mmi1.ports['o4'].center[1]) + 2*min_bending),
            (float(mmi2.ports['o2'].center[0]) - min_bending, float(mmi1.ports['o4'].center[1]) + 2*min_bending),
            (float(mmi2.ports['o2'].center[0]) - min_bending, float(mmi2.ports['o2'].center[1])),
        ]
    )


#--------------- Heater---------------------
    if upper_htr:
        via_left_up = c.add_ref(gf.components.compass(size=(3, 3), layer=LAYER.VIA2))
        via_left_up.move((mmi1.ports['o4'].center[0] + 2*min_bending, mmi1.ports['o4'].center[1] + 2*min_bending))
        via_right_up = c.add_ref(gf.components.compass(size=(3, 3), layer=LAYER.VIA2))
        via_right_up.move((mmi2.ports['o2'].center[0] - 2*min_bending, mmi2.ports['o2'].center[1] + 2*min_bending))

        htr_up = c.add_ref(gf.components.rectangle(size = (htr_length + 10, htr_width), layer = "HTR"))
        htr_up.move((via_left_up.ports['e1'].center[0] - 3.5, via_left_up.ports['e1'].center[1] - htr_width/2))
        htr_patch_left_up = c.add_ref(gf.components.rectangle(size=(10, 10), layer='HTR'))
        htr_patch_left_up.center= via_left_up.center
        htr_patch_right_up = c.add_ref(gf.components.rectangle(size=(10, 10), layer='HTR'))
        htr_patch_right_up.center= via_right_up.center

        MT_patch_left_up = c.add_ref(gf.components.rectangle(size=(10, 10), layer='MT2'))
        MT_patch_left_up.center= via_left_up.center
        MT_patch_right_up = c.add_ref(gf.components.rectangle(size=(10, 10), layer='MT2'))
        MT_patch_right_up.center= via_right_up.center

    if lower_htr:
        via_left_down = c.add_ref(gf.components.compass(size=(3, 3), layer=LAYER.VIA2))
        via_left_down.move((mmi1.ports['o3'].center[0] + 2*min_bending, mmi1.ports['o3'].center[1] - 2*min_bending))
        via_right_down = c.add_ref(gf.components.compass(size=(3, 3), layer=LAYER.VIA2))
        via_right_down.move((mmi2.ports['o1'].center[0] - 2*min_bending, mmi2.ports['o1'].center[1] - 2*min_bending))

        htr_down = c.add_ref(gf.components.rectangle(size = (htr_length + 10, htr_width), layer = "HTR"))
        htr_down.move((via_left_down.ports['e1'].center[0] - 3.5, via_left_down.ports['e1'].center[1] - htr_width/2))
        htr_patch_left_down = c.add_ref(gf.components.rectangle(size=(10, 10), layer='HTR'))
        htr_patch_left_down.center= via_left_down.center
        htr_patch_right_down = c.add_ref(gf.components.rectangle(size=(10, 10), layer='HTR'))
        htr_patch_right_down.center= via_right_down.center

        MT_patch_left_down = c.add_ref(gf.components.rectangle(size=(10, 10), layer='MT2'))
        MT_patch_left_down.center= via_left_down.center
        MT_patch_right_down = c.add_ref(gf.components.rectangle(size=(10, 10), layer='MT2'))
        MT_patch_right_down.center= via_right_down.center


    #---------------------- Ports -------------------
    c.add_port('o1', port = mmi1.ports['o1'])
    c.add_port('o2', port = mmi1.ports['o2'])
    c.add_port('o3', port = mmi2.ports['o3'])
    c.add_port('o4', port = mmi2.ports['o4'])
    return c
