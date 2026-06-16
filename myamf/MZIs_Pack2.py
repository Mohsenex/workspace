import gdsfactory as gf
from .Rib_MZI import Rib_MZI
from .SiN_MZI import SiN_MZI
from .via_MZI import via_MZI
from .strip_MZI import strip_MZI
from .SiN_1250_MZI import SiN_1250_MZI

@gf.cell
def MZIs_Pack2()->gf.Component:
    c = gf.Component()
    
    strip = c.add_ref(strip_MZI(gap = 100, dl = 62.017, cross_section = "strip"))
    strip.move((0, 0))

    Rib1 = c.add_ref(Rib_MZI(gap = 180, dl= 59.877, cross_section = "strip", taper_length= 30, strip_width = 0.5))
    Rib1.move((0, 100))
    Rib2 = c.add_ref(Rib_MZI(gap = 180, dl= 52.004, cross_section = "strip", taper_length= 30, strip_width = 0.55))
    Rib2.move((0, 100 * 2))

    SiN = c.add_ref(SiN_MZI(gap = 300, dl = 97.055, cross_section = "strip"))
    SiN.move((400, -100))
    SiN_1250 = c.add_ref(SiN_MZI(gap = 400, dl = 95.437, cross_section = "strip"))
    SiN_1250.move((400, -350))


    via = c.add_ref(via_MZI())
    via.move((1300, 0))


    return c
