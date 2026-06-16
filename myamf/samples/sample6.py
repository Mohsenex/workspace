"""Pack."""

import gdsfactory as gf
from amf.chp import LAYER


@gf.cell
def sample6_cross_section():
    p = gf.path.straight()

    # Add a few "sections" to the cross-section
    s0 = gf.Section(width=1, offset=0, layer=LAYER.WG, port_names=("o1", "o2"))
    s1 = gf.Section(width=2, offset=2, layer=LAYER.NIM)
    s2 = gf.Section(width=2, offset=-2, layer=LAYER.PIM)
    x = gf.CrossSection(sections=(s0, s1, s2))

    return gf.path.extrude(p, cross_section=x)
