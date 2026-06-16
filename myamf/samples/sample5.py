"""Pack."""

import gdsfactory as gf
from amf.chp import LAYER


@gf.cell
def sample5_path():
    p = gf.Path()
    p += gf.path.arc(radius=10, angle=90)  # Circular arc
    p += gf.path.straight(length=10)  # Straight section
    p += gf.path.euler(radius=3, angle=-90)  # Euler bend (aka "racetrack" curve)
    p += gf.path.straight(length=40)
    p += gf.path.arc(radius=8, angle=-45)
    p += gf.path.straight(length=10)
    p += gf.path.arc(radius=8, angle=45)
    p += gf.path.straight(length=10)
    return p.extrude(layer=LAYER.WG, width=1.5)
