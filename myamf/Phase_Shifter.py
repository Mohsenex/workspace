import gdsfactory as gf

import amf.chp as pdk
from amf.chp.tech import LAYER, TECH

from amf.chp.cells.tapers import taper_strip_to_ridge
from gdsfactory.components import L


@gf.cell
def Phase_Shifter(
    l: float = 200,
    taper_length: float = 40,
    strip_width: float = 0.5,
) -> gf.Component:
     
    c = gf.Component()
     
    
    strip2rib_1 = c.add_ref(taper_strip_to_ridge(
    length=taper_length,
    width1=0.5,   # strip width
    width2=strip_width,   # rib core width
    w_slab2=6.5,  # matches AMF rib slab width
    ))
    
    strip2rib_2 = c.add_ref(taper_strip_to_ridge(
    length=taper_length,
    width1=0.5,   # strip width
    width2=strip_width,   # rib core width
    w_slab2=6.5,  # matches AMF rib slab width
    ))
    strip2rib_2.mirror_x()
    strip2rib_2.move((l + 2*taper_length, 0))

    #--------------- Rib section:
    rib = gf.routing.route_single(
        c,
        port1=strip2rib_1.ports["o2"],
        port2=strip2rib_2.ports["o2"],
        cross_section='rib',
    )

    #---------- Dopings ---------------
    p_plus = c.add_ref(gf.components.rectangle(size = (l, 2.3), layer = LAYER.IPD))
    p_plus.xmin = strip2rib_1.xmax
    p_plus.movey(strip_width/2 + 0.7)

    p_plus2 = c.add_ref(gf.components.rectangle(size = (l, 2), layer = LAYER.PCONT))
    p_plus2.xmin = strip2rib_1.xmax
    p_plus2.movey(strip_width/2 + 1)

    n_plus = c.add_ref(gf.components.rectangle(size = (l, 2.3), layer = LAYER.IND))
    n_plus.xmin = strip2rib_1.xmax
    n_plus.movey(-strip_width/2 - 0.7 -2.3)

    n_plus2 = c.add_ref(gf.components.rectangle(size = (l, 2), layer = LAYER.NCONT))
    n_plus2.xmin = strip2rib_1.xmax
    n_plus2.movey(-strip_width/2 - 1 -2)

    #---------- Via1 ---------------
    via1_up = c.add_ref(gf.components.rectangle(size = (l-1, 1.5), layer = LAYER.VIA1))
    via1_up.center = p_plus2.center

    via1_low = c.add_ref(gf.components.rectangle(size = (l-1, 1.5), layer = LAYER.VIA1))
    via1_low.center = n_plus2.center

#---------- Metal1 ---------------
    mt1_up = c.add_ref(gf.components.rectangle(size = (l + 4, 8), layer = LAYER.MT1))
    mt1_up.xmin = strip2rib_1.xmax - 2
    mt1_up.ymin = via1_up.ymin - 0.5

    mt1_low = c.add_ref(gf.components.rectangle(size = (l + 4, 8), layer = LAYER.MT1))
    mt1_low.xmin = strip2rib_1.xmax - 2
    mt1_low.ymax = via1_low.ymax + 0.5
    

    #---------- Via2 ---------------
    via2_up = c.add_ref(gf.components.rectangle(size = (l, 2), layer = LAYER.VIA2))
    via2_up.xmin = strip2rib_1.xmax
    via2_up.ymin = via1_up.ymax + 2

    via2_low = c.add_ref(gf.components.rectangle(size = (l, 2), layer = LAYER.VIA2))
    via2_low.xmin = strip2rib_1.xmax
    via2_low.ymax = via1_low.ymin - 2
    

    #---------- Metal2 ---------------
    mt2_up = c.add_ref(gf.components.rectangle(size = (l+4, 6), layer = LAYER.MT2))
    mt2_up.xmin = strip2rib_1.xmax - 2
    mt2_up.ymax = mt1_up.ymax

    mt2_low = c.add_ref(gf.components.rectangle(size = (l+4, 6), layer = LAYER.MT2))
    mt2_low.xmin = strip2rib_1.xmax - 2
    mt2_low.ymin = mt1_low.ymin

    c.add_port('o1', port = strip2rib_1.ports['o1'])
    c.add_port('o2', port = strip2rib_2.ports['o1'])

    c.add_port('e1', center=mt2_up.center,  width=mt2_up.xsize,  orientation=90,  port_type='electrical', layer=LAYER.MT2)
    c.add_port('e2', center=mt2_low.center, width=mt2_low.xsize, orientation=270, port_type='electrical', layer=LAYER.MT2)

    return c
