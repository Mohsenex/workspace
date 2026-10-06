import gdsfactory as gf
from amf.chp.tech import LAYER, TECH

@gf.cell
def MMI_Placeholder()->gf.Component:
    c = gf.Component()
    b1 = c.add_ref(gf.components.rectangle(size = (100, 1), layer = 'WG_SIN'))
    b2 = c.add_ref(gf.components.rectangle(size = (100, 1), layer = 'WG_SIN'))
    b2.movey(2)
    # add references or polygons here...
    c.add_port('o1', port = b1.ports['e1'], port_type='optical')
    c.add_port('o2', port = b2.ports['e1'], port_type='optical')
    c.add_port('o3', port = b1.ports['e3'], port_type='optical')
    c.add_port('o4', port = b2.ports['e3'], port_type='optical')
    return c
