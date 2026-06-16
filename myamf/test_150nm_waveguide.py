import gdsfactory as gf
from amf.chp import LAYER

@gf.cell
def test_150nm_waveguide()->gf.Component:
    c = gf.Component()
    
    rect1 = c.add_ref(gf.components.rectangle(size = (20, 4), layer = LAYER.GRAT))
    rect1.movey(-4/2)
    rect2 = c.add_ref(gf.components.rectangle(size = (20, 6.5), layer = LAYER.RIB))
    rect2.movey(-6.5/2)
    rect3 = c.add_ref(gf.components.rectangle(size = (20, 0.7), layer = LAYER.WG))
    rect3.movey(-0.7/2)
    # gf.routing.route_single(
    #     c,
    #     port1 = rect1.ports['e1'],
    #     port2 = rect1.ports['e3'],
    #     cross_section = 'rib',
    # )
    return c
