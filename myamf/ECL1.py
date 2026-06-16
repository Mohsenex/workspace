import gdsfactory as gf
from gdsfactory.pdk import get_active_pdk

from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_LSiN2SOISSC_Cband_v5p0)
from amf.config import PATH
# from amf.chp.tech import LAYER, TECH
from amf.import_gds import import_gds


from .Balanced_PD import Balanced_PD


gdsdir = PATH.gds_chp

N_FIBERS = 22
PITCH = 127.0  # um
DIE_SIZE = (7400, 3000)


@gf.cell
def ECL1() -> gf.Component:
    c = gf.Component()
    pdk = get_active_pdk()

    die = c.add_ref(pdk.get_component("die_frame_full", size=DIE_SIZE))

    
    #---------------------------------------------------------------------------------------
    # PADs — 38 individual pads, 125 µm pitch, centered at top of die
    #---------------------------------------------------------------------------------------
    N_PADS = 30
    PAD_PITCH = 125.0
    pad_cell = pdk.get_component("pad")

    pads = []
    x_start = die.xmin + 150  #die.x - (N_PADS - 1) * PAD_PITCH / 2 + 1400
    for i in range(N_PADS):
        p = c.add_ref(pad_cell)
        p.x = x_start + i * PAD_PITCH
        p.ymax = die.ymax - 50
        pads.append(p)

    # Access individual pads as: pads[0], pads[1], ..., pads[37]
    # Each pad has ports: e1 (west), e2 (north), e3 (east), e4 (south)

   

    #---------------------------------------------------------------------------------------
    # ECL1 
    #---------------------------------------------------------------------------------------

    ecl1 = gf.import_gds("/workspace/myamf/gds/FonexQuietXECL_InsideOut_Hybrid_V2026_2.gds")
    # SiN Ports:
    ecl1.add_port(name="o1", center=(416.054, 209.414), width=1.0, orientation=0, layer='WG_SIN')
   
    # Si Ports:
    ecl1.add_port(name="o2", center=(-452.946, -89.91), width=0.5, orientation=270, layer='WG')
    ecl1.add_port(name="o3", center=(789.054, -179.91), width=0.5, orientation=0, layer='WG')
    ecl1.add_port(name="o4", center=(789.054, -178.576), width=0.5, orientation=0, layer='WG')
    ecl1.add_port(name="o5", center=(503.36, 490.21), width=0.5, orientation=90, layer='WG')
    ecl1.add_port(name="o6", center=(-479.84, 541.118), width=0.5, orientation=180, layer='WG')
    ecl1.add_port(name="o7", center=(-479.84, 387.968), width=0.5, orientation=180, layer='WG')
   
    # Metal 2 Ports:
    ecl1.add_port(name="e1", center=(-322.306, -93.266), width=20, orientation=270,  layer="MT2", port_type="electrical")
    ecl1.add_port(name="e2", center=(-235.616, -109.506), width=20, orientation=270,  layer="MT2", port_type="electrical")
    ecl1.add_port(name="e3", center=(-322.306, -17.557), width=20, orientation=90,  layer="MT2", port_type="electrical")
    ecl1.add_port(name="e4", center=(-235.616, -34.957), width=20, orientation=90,  layer="MT2", port_type="electrical")
    ecl1.add_port(name="e5", center=(-316.16, 618.378), width=20, orientation=90,  layer="MT2", port_type="electrical")
    ecl1.add_port(name="e6", center=(-248.68, 618.378), width=20, orientation=90,  layer="MT2", port_type="electrical")
    ecl1.add_port(name="e7", center=(-169.98, 618.76), width=20, orientation=90,  layer="MT2", port_type="electrical")
    ecl1.add_port(name="e8", center=(-94.54, 618.378), width=20, orientation=90,  layer="MT2", port_type="electrical")

    ecl1 = c.add_ref(ecl1)
    ecl1.xmin = die.xmin - 6
    ecl1.movey(700)
    return c

    