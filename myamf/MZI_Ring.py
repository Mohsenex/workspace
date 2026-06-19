import gdsfactory as gf
from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_Si2X2MMI_Cband_v5p0,
    AMF_300LSOI_LSiN2SOISSC_Cband_v5p0,
)
from amf.chp.tech import LAYER, TECH
from amf.import_gds import import_gds

@gf.cell
def MZI_Ring(
    l: float = 800, # distance between splitter and combiner
    gap: float = 0.35,
    coupling_length: float = 21, 
    coupling_radius: float = 100,
    wg_width: float = 1.25,
    taper_length: float = 30,
    separation: float = 5.25,
    min_bend_radius: float = 100 *2,
    htr_length: float = 300,
    htr_radius = 250,
    number_of_loops: float = 33,
    npoints: float = 20000,
)->gf.Component:
    c = gf.Component()
    #---------------------------------------------------------------
    # MZI
    #---------------------------------------------------------------
    splitter = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    combiner = c.add_ref(AMF_300LSOI_Si2X2MMI_Cband_v5p0())
    combiner.move((55 + l, 0))

    # for the upper arm:
    via1 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via1.xmin = splitter.xmax + 20
    via1.movey(splitter.ports['o2'].center[1] + 25)

    via2 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via2.mirror_x()
    via2.xmax = combiner.xmin - 40 - htr_length
    via2.movey(splitter.ports['o2'].center[1] + 25)

    taper1 = c.add_ref(gf.components.taper(
        length= taper_length,        # taper length in µm (adjust as needed)
        width1=1.0,         # 1000 nm → 1.0 µm
        width2= wg_width,        # 1250 nm → 1.25 µm
        cross_section="nitride",
    ))
    taper1.move((via1.ports['o2'].center[0], via1.ports['o2'].center[1]))

    taper2 = c.add_ref(gf.components.taper(
        length= taper_length,        # taper length in µm (adjust as needed)
        width1=1.0,         # 1000 nm → 1.0 µm
        width2= wg_width,        # 1250 nm → 1.25 µm
        cross_section="nitride",
    ))
    taper2.mirror_x()
    taper2.xmax = via2.xmin
    taper2.movey(via2.ports['o2'].center[1])

    # for the lower arm:
    via3 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via3.xmin = splitter.xmax + 20
    via3.movey(splitter.ports['o3'].center[1] - 25)

    via4 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via4.mirror_x()
    via4.xmax = combiner.xmin - 40 - htr_length
    via4.movey(splitter.ports['o3'].center[1] - 25)

    taper3 = c.add_ref(gf.components.taper(
        length= taper_length,        # taper length in µm (adjust as needed)
        width1=1.0,         # 1000 nm → 1.0 µm
        width2= wg_width,        # 1250 nm → 1.25 µm
        cross_section="nitride",
    ))
    taper3.move((via3.ports['o2'].center[0], via3.ports['o2'].center[1]))

    taper4 = c.add_ref(gf.components.taper(
        length= taper_length,        # taper length in µm (adjust as needed)
        width1=1.0,         # 1000 nm → 1.0 µm
        width2= wg_width,        # 1250 nm → 1.25 µm
        cross_section="nitride",
    ))
    taper4.mirror_x()
    taper4.xmax = via4.xmin
    taper4.movey(via4.ports['o2'].center[1])


    gf.routing.route_single(
        c,
        port1 = splitter.ports['o2'],
        port2 = via1.ports['o1'],
        cross_section = 'strip',
    )
    gf.routing.route_single(
        c,
        port1 = via2.ports['o1'],
        port2 = combiner.ports['o2'],
        cross_section = 'strip',
        waypoints = [
            (float(via2.ports['o1'].center[0] + 30 + htr_length), float(via2.ports['o1'].center[1] )),
            (float(via2.ports['o1'].center[0] + 30 + htr_length), float(combiner.ports['o2'].center[1] )),
        ],
    )

    xs_sin = gf.cross_section.strip(
    width= wg_width,
    radius=25,
    radius_min=25,
    layer=LAYER.WG_SIN,
    )

    gf.routing.route_single(
        c,
        port1 = taper1.ports['o2'],
        port2 = taper2.ports['o2'],
        cross_section = xs_sin,
    )


    gf.routing.route_single(
        c,
        port1 = splitter.ports['o3'],
        port2 = via3.ports['o1'],
        cross_section = 'strip',
    )
    gf.routing.route_single(
        c,
        port1 = via4.ports['o1'],
        port2 = combiner.ports['o1'],
        cross_section = 'strip',
        waypoints = [
            (float(via4.ports['o1'].center[0] + 30 + htr_length), float(via4.ports['o1'].center[1] )),
            (float(via4.ports['o1'].center[0] + 30 + htr_length), float(combiner.ports['o1'].center[1] )),
        ],
    )

    gf.routing.route_single(
        c,
        port1 = taper3.ports['o2'],
        port2 = taper4.ports['o2'],
        cross_section = xs_sin,
    )
    #----------------------------------------------------------------------
    # MZI Heater
    #----------------------------------------------------------------------
    htr = c.add_ref(gf.components.rectangle(size = (htr_length, 10), layer = LAYER.HTR))
    htr.xmax = combiner.xmin - 30 
    htr.ymin = splitter.ports['o3'].center[1] - 30

    htr_patch_right = c.add_ref(gf.components.rectangle(size=(8, 8), layer=LAYER.HTR))
    htr_patch_right.xmax= htr.xmax
    htr_patch_right.ymax= htr.ymax
    htr_patch_left = c.add_ref(gf.components.rectangle(size=(8, 8), layer=LAYER.HTR))
    htr_patch_left.xmin= htr.xmin
    htr_patch_left.ymax= htr.ymax

    via_patch_right = c.add_ref(gf.components.rectangle(size=(4, 4), layer=LAYER.VIA2))
    via_patch_right.center= htr_patch_right.center
    via_patch_left = c.add_ref(gf.components.rectangle(size=(4, 4), layer=LAYER.VIA2))
    via_patch_left.center= htr_patch_left.center

    mt_patch_right = c.add_ref(gf.components.rectangle(size=(12, 12), layer=LAYER.MT2))
    mt_patch_right.center= htr_patch_right.center
    mt_patch_left = c.add_ref(gf.components.rectangle(size=(12, 12), layer=LAYER.MT2))
    mt_patch_left.center= htr_patch_left.center

    #---------------------------------------------------------------------
    # Spiral
    #---------------------------------------------------------------------
    bend=dict(component='bend_euler', settings=dict(p=0.9))
    # spiral = c.add_ref(gf.components.spiral_double(min_bend_radius=min_bend_radius, separation=separation, number_of_loops=number_of_loops, npoints=npoints, cross_section=xs_sin, bend=bend))
    spiral = gf.import_gds("/workspace/myamf/gds/Ring_WL.gds", skip_new_cells=True)
    spiral.add_port(name="o1", center=(0, 546.5), width=1.25, orientation=180, layer='WG_SIN')
    spiral.add_port(name="o2", center=(0, -546.5), width=1.25, orientation=0, layer='WG_SIN')
    spiral = c.add_ref(spiral)
    spiral.ymin = taper1.ports['o2'].center[1] + wg_width/2 + gap + 2 * coupling_radius + 61.71 + 0.350
    spiral.movex(taper1.ports['o2'].center[0] + (taper2.ports['o2'].center[0] - taper1.ports['o2'].center[0])/2 )
    
    tiny_ring = gf.Path()
    tiny_ring += gf.path.euler(radius=coupling_radius, angle=-180, p=0.9)
    tiny_ring += gf.path.straight(length=coupling_length)
    tiny_ring += gf.path.euler(radius=coupling_radius, angle=-90, p=0.9)
    tiny_ring += gf.path.euler(radius=coupling_radius, angle=90, p=0.7)
    tiny_ring_wg = tiny_ring.extrude(xs_sin)
    t_ring = c.add_ref(tiny_ring_wg)
    t_ring.move((spiral.ports['o2'].center[0], spiral.ports['o2'].center[1]))

    gf.routing.route_single(
        c,
        port1 = t_ring.ports['o2'],
        port2 = spiral.ports['o1'],
        cross_section =  gf.cross_section.strip(width= wg_width, radius=190, layer=LAYER.WG_SIN),
        waypoints = [
            (spiral.xmin - separation, t_ring.ports['o2'].center[1]),
            # (spiral.xmin - separation, spiral.ymin + (spiral.ymax - spiral.ymin)/2 ),
            (spiral.xmin - separation, spiral.ports['o1'].center[1]),
        ],
    )
    
    #------------ Heater ---------------------------------
    xs_htr = gf.cross_section.strip(
    width= 20,
    radius=25,
    radius_min=25,
    layer=LAYER.HTR,
    )
    
    spiral_htr = gf.Path()
    spiral_htr += gf.path.arc(radius=htr_radius, angle=90) 
    spiral_htr = c.add_ref(spiral_htr.extrude(xs_htr))
    spiral_htr.ymin = spiral.center[1] - htr_radius
    spiral_htr.xmin = spiral.center[0] 
    # spiral_htr.rotate(90)
    # spiral_htr.move(spiral.center)
    spiral_htr_patch_right = c.add_ref(gf.components.rectangle(size=(8, 8), layer=LAYER.HTR))
    spiral_htr_patch_right.move(spiral_htr.ports['o1'].center)
    
    spiral_htr_patch_left = c.add_ref(gf.components.rectangle(size=(8, 8), layer=LAYER.HTR))
    spiral_htr_patch_left.move(spiral_htr.ports['o2'].center )
    spiral_htr_patch_left.movey(-12)
    

    spiral_via_patch_right = c.add_ref(gf.components.rectangle(size=(4, 4), layer=LAYER.VIA2))
    spiral_via_patch_right.center= spiral_htr_patch_right.center
    spiral_via_patch_left = c.add_ref(gf.components.rectangle(size=(4, 4), layer=LAYER.VIA2))
    spiral_via_patch_left.center= spiral_htr_patch_left.center

    spiral_mt_patch_right = c.add_ref(gf.components.rectangle(size=(12, 12), layer=LAYER.MT2))
    spiral_mt_patch_right.center= spiral_htr_patch_right.center
    spiral_mt_patch_left = c.add_ref(gf.components.rectangle(size=(12, 12), layer=LAYER.MT2))
    spiral_mt_patch_left.center= spiral_htr_patch_left.center

    #--------- Deep trench -----------------
    deeptrench = c.add_ref(gf.components.rectangle(size = (l - 80, 20), layer = LAYER.DTR))
    deeptrench.xmin = splitter.xmax + 40
    deeptrench.y = splitter.y

    #---------- Add Ports-------------------
    c.add_port('o1', port = splitter.ports['o1'])
    c.add_port('o2', port = combiner.ports['o3'])
    c.add_port('o3', port = combiner.ports['o4'])

    c.add_port('e1', port = spiral_mt_patch_right.ports['e4'])
    c.add_port('e2', port = spiral_mt_patch_left.ports['e4'])
    c.add_port('e3', port = mt_patch_right.ports['e4'])
    c.add_port('e4', port = mt_patch_left.ports['e4'])

    return c
