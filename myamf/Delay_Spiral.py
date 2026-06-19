from turtle import width

import gdsfactory as gf
from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_Si2X2MMI_Cband_v5p0,
    AMF_300LSOI_LSiN2SOISSC_Cband_v5p0,
    AMF_300LSOI_SiVOA_Cband_v5p0,
)
import amf.chp as pdk
from amf.chp.tech import LAYER
from amf.import_gds import import_gds

@gf.cell
def Delay_Spiral(
    width = 3, # width of SiN waveguide
    taper_length = 200, # length of the transition from standard SiN to customized width
    min_bend_radius=270 * 2, 
    separation: float =6.5, 
    number_of_loops=27, 
    htr_radius = 650,
    mzi_htr_length: float = 300,
    npoints=20000, 
    sps_gap = 15, #  gap between the two spirals
)->gf.Component:
    c = gf.Component()
    
    # Defining the cross section for 1.25 um SiN:
    xs_sin = gf.cross_section.strip(
    width=width,
    radius=25,
    radius_min=25,
    layer=LAYER.WG_SIN,
    )
    #------------------------------------------------------------------------------
    # Spiral
    #------------------------------------------------------------------------------
    cross_section=gf.cross_section.strip(width = width)
    bend=dict(component='bend_euler', settings=dict(p=0))
    # sp1 = c.add_ref(gf.components.spiral_double(min_bend_radius=min_bend_radius, separation=separation, number_of_loops=number_of_loops, npoints=npoints, cross_section=xs_sin, bend=bend))
    sp = gf.import_gds("/workspace/myamf/gds/Delay_WL.gds")
    sp.add_port(name="o1", center=(0, 891), width=3, orientation=180, layer='WG_SIN')
    sp.add_port(name="o2", center=(0, -891), width=3, orientation=0, layer='WG_SIN')
    sp1 = c.add_ref(sp)
    
    # sp2 = c.add_ref(gf.components.spiral_double(min_bend_radius=min_bend_radius, separation=separation, number_of_loops=number_of_loops, npoints=npoints, cross_section=xs_sin, bend=bend))
    sp2 = c.add_ref(sp)
    spiral_width = 2 * (min_bend_radius + 2 * separation * number_of_loops)
    sp2_offset = spiral_width + sps_gap
    sp2.movex(sp2_offset)

    # sp1.o1 is at (0, +half_h) facing LEFT (180°)
    # sp2.o2 is at (sp2_offset, -half_h) facing RIGHT (0°)
    # Route: go left from sp1.o1, drop below both spirals, come in from right to sp2.o2
    spiral_half_height = min_bend_radius + 2 * separation * number_of_loops
    clearance = min_bend_radius  # enough room to bend without touching the spiral

    sp1_sp2_connection = gf.routing.route_single(
        c,
        port1=sp1.ports["o2"],
        port2=sp2.ports["o1"],
        cross_section=gf.cross_section.strip(radius = spiral_half_height, width = width, layer=LAYER.WG_SIN,),
        waypoints=[
            (spiral_half_height + sps_gap/2, sp1.ports["o2"].center[1]),
            (spiral_half_height + sps_gap/2, spiral_half_height ),
        ],
    )

    #-------------------------------------------------------------------------------
    # Splitter and combiner
    #-------------------------------------------------------------------------------
    splitter = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    splitter.move([-spiral_half_height, spiral_half_height + 0.9])

    via1 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via1.move([-spiral_half_height + 80, spiral_half_height])

    taper1 = c.add_ref(gf.components.taper(
        length=taper_length,        # taper length in µm (adjust as needed)
        width1=1.0,         # 1000 nm → 1.0 µm
        width2=width,        # 1250 nm → 1.25 µm
        cross_section="nitride",
    ))
    taper1.move([-spiral_half_height + 80 + 121, spiral_half_height])

    via2 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via2.move([1.5 * spiral_half_height , spiral_half_height + 10])

    taper2 = c.add_ref(gf.components.taper(
        length=taper_length,        # taper length in µm (adjust as needed)
        width1=1.0,         # 1000 nm → 1.0 µm
        width2=width,        # 1250 nm → 1.25 µm
        cross_section="nitride",
    ))
    taper2.move([1.5 * spiral_half_height + 121 , spiral_half_height + 10])

    voa = c.add_ref(AMF_300LSOI_SiVOA_Cband_v5p0())
    voa.mirror_y()
    voa.move([spiral_half_height -310/2, spiral_half_height +1.8])

    combiner = c.add_ref(AMF_300LSOI_Si2X2MMI_Cband_v5p0())
    combiner.rotate(90)
    combiner.move([spiral_half_height + 310/2 + 40, spiral_half_height+ 30 ])


    gf.routing.route_single(
        c,
        port1 = splitter.ports['o3'],
        port2 = via1.ports['o1'],
        cross_section = 'strip',
    )
    gf.routing.route_single(
        c,
        port1 = taper1.ports['o2'],
        port2 = sp1.ports['o1'],
        cross_section = xs_sin,
    )

    gf.routing.route_single(
        c,
        port1 = splitter.ports['o2'],
        port2 = voa.ports['o1'],
        cross_section = 'strip',
        waypoints=[
            (splitter.ports["o2"].center[0] + 20, splitter.ports["o2"].center[1]),
            (splitter.ports["o2"].center[0] + 20, splitter.ports["o2"].center[1] +20),
            (splitter.ports["o2"].center[0] + 20 + 1.2 * spiral_half_height, splitter.ports["o2"].center[1] +20),
            (splitter.ports["o2"].center[0] + 20 + 1.2 * spiral_half_height, splitter.ports["o2"].center[1] ),
        ],
    )

    gf.routing.route_single(
        c,
        port1 = sp2.ports['o2'],
        port2 = taper2.ports['o2'],
        cross_section = gf.cross_section.strip(radius = spiral_half_height, width = width, layer=LAYER.WG_SIN,),
        waypoints=[
            (sp2.ports["o2"].center[0] + spiral_half_height + separation, sp2.ports["o2"].center[1]),
            (sp2.ports["o2"].center[0] + spiral_half_height + separation, taper2.ports["o2"].center[1]),
        ],
    )

    gf.routing.route_single(
        c,
        port1 = via2.ports['o1'],
        port2 = combiner.ports['o1'],
        cross_section = 'strip',
    )

    gf.routing.route_single(
        c,
        port1 = voa.ports['o2'],
        port2 = combiner.ports['o2'],
        cross_section = 'strip',
    )

    #----------------------------------------------------------------------
    # MZI Heater
    #----------------------------------------------------------------------
    htr = c.add_ref(gf.components.rectangle(size = (mzi_htr_length, 10), layer = LAYER.HTR))
    htr.xmax = voa.xmin - 50 
    htr.ymin = voa.ports['o1'].center[1] - 5

    htr_patch_right = c.add_ref(gf.components.rectangle(size=(8, 8), layer=LAYER.HTR))
    htr_patch_right.xmax= htr.xmax
    htr_patch_right.ymax= htr.ymax 
    htr_patch_left = c.add_ref(gf.components.rectangle(size=(8, 8), layer=LAYER.HTR))
    htr_patch_left.xmin= htr.xmin
    htr_patch_left.ymin= htr.ymax -10

    via_patch_right = c.add_ref(gf.components.rectangle(size=(4, 4), layer=LAYER.VIA2))
    via_patch_right.center= htr_patch_right.center
    via_patch_left = c.add_ref(gf.components.rectangle(size=(4, 4), layer=LAYER.VIA2))
    via_patch_left.center= htr_patch_left.center

    mt_patch_right = c.add_ref(gf.components.rectangle(size=(12, 12), layer=LAYER.MT2))
    mt_patch_right.center= htr_patch_right.center
    mt_patch_left = c.add_ref(gf.components.rectangle(size=(12, 12), layer=LAYER.MT2))
    mt_patch_left.center= htr_patch_left.center

    #------------ Heater ---------------------------------
    xs_htr = gf.cross_section.strip(
    width= 20,
    radius=25,
    radius_min=25,
    layer=LAYER.HTR,
    )
    
    spiral_htr = gf.Path()
    spiral_htr += gf.path.arc(radius=htr_radius, angle=-90) 
    spiral_htr.rotate(90)
    spiral_htr = c.add_ref(spiral_htr.extrude(xs_htr))
    spiral_htr.ymin = sp1.center[1] #- htr_radius
    spiral_htr.xmin = sp1.center[0] - htr_radius
    # spiral_htr.rotate(90)
    # spiral_htr.move(spiral.center)
    spiral_htr_patch_right = c.add_ref(gf.components.rectangle(size=(8, 8), layer=LAYER.HTR))
    spiral_htr_patch_right.move(spiral_htr.ports['o1'].center)
    spiral_htr_patch_left = c.add_ref(gf.components.rectangle(size=(8, 8), layer=LAYER.HTR))
    spiral_htr_patch_left.move(spiral_htr.ports['o2'].center)
    spiral_htr_patch_left.move((-10, -2.5))    

    spiral_via_patch_right = c.add_ref(gf.components.rectangle(size=(4, 4), layer=LAYER.VIA2))
    spiral_via_patch_right.center= spiral_htr_patch_right.center
    spiral_via_patch_left = c.add_ref(gf.components.rectangle(size=(4, 4), layer=LAYER.VIA2))
    spiral_via_patch_left.center= spiral_htr_patch_left.center

    spiral_mt_patch_right = c.add_ref(gf.components.rectangle(size=(12, 12), layer=LAYER.MT2))
    spiral_mt_patch_right.center= spiral_htr_patch_right.center
    spiral_mt_patch_left = c.add_ref(gf.components.rectangle(size=(12, 12), layer=LAYER.MT2))
    spiral_mt_patch_left.center= spiral_htr_patch_left.center


    #--------------- Adding Ports-------------------------
    c.add_port('o1', port = splitter.ports['o1'])
    c.add_port('o2', port = combiner.ports['o3'])
    c.add_port('o3', port = combiner.ports['o4'])

    c.add_port('e1', port = spiral_mt_patch_right.ports['e2'])
    c.add_port('e2', port = spiral_mt_patch_left.ports['e2'])
    c.add_port('e3', port = mt_patch_right.ports['e2'])
    c.add_port('e4', port = mt_patch_left.ports['e2'])
    c.add_port('e5', port = voa.ports['e3'])
    c.add_port('e6', port = voa.ports['e2'])
    c.add_port('e7', port = voa.ports['e1'])
    return c
