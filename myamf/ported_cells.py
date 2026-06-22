import gdsfactory as gf
from gdsfactory.pdk import get_active_pdk
from amf.chp.cells.fixed import (
    AMF_300LSOI_Si2X2MMI_Cband_v5p0,
    AMF_300LSOI_LSiN2SOISSC_Cband_v5p0,
)

# ---------------------------------------------------------------------------
# AMF PDK 5.0 fixed cells that ship WITHOUT optical ports must have ports
# re-attached before they can be used with gdsfactory routing.
#
# Confirmed against AMF-QP-RND-068 Rev 2 and the cell geometry read off the BB
# optical-port layers (BB_OP_SI = 1010 -> Si layer 10/RIB;
# BB_OP_SIN = 1011 -> SiN layer 50/WG_SIN).
#
# - SSC and 2x2 MMI are PORTLESS in this PDK build      -> wrapped here.
# - 1x2 MMI (and edge coupler, PowMonitor, GC, VOA ...) HAVE native ports via
#   pdk.get_component(), so they are fetched directly.
# ---------------------------------------------------------------------------


@gf.cell
def ssc_via() -> gf.Component:
    """AMF_300LSOI_LSiN2SOISSC (SiN<->Si SSC) with ports attached.

    o1 = Si  side, (0, 0),   width 0.5 um, faces west  (RIB    / layer 10)
    o2 = SiN side, (121, 0), width 1.0 um, faces east  (WG_SIN / layer 50)
    """
    c = gf.Component()
    c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    c.add_port(name="o1", center=(0.0, 0.0),   width=0.5, orientation=180, layer="RIB")
    c.add_port(name="o2", center=(121.0, 0.0), width=1.0, orientation=0,   layer="WG_SIN")
    return c


def mmi_1x2() -> gf.Component:
    """AMF_300LSOI_Si1X2MMI - has native ports o1/o2/o3 via the PDK."""
    return get_active_pdk().get_component("AMF_300LSOI_Si1X2MMI_Cband_v5p0")


@gf.cell
def mmi_2x2(flip_lr: bool = False, flip_tb: bool = False) -> gf.Component:
    """AMF_300LSOI_Si2X2MMI (2x2 MMI) with ports attached.

    Geometry: bbox 0..75 x -5..5; Si ports 0.5 um on layer 1010 (-> RIB/10).
    AMF manual Table 10: opt_1_si/opt_2_si = inputs (west),
                         opt_3_si/opt_4_si = outputs (east).

    Default (matches AMF doc):
        o1 = west top    (0,  +0.667)        o3 = east top    (75, +0.667)
        o2 = west bottom (0,  -0.667)        o4 = east bottom (75, -0.667)

    flip_lr : mirror left<->right. Inputs/outputs swap sides, so o1/o2 land on
              the east face and o3/o4 on the west. Use this if your colleague's
              convention numbered the 2x2 the other way and routes come out
              reversed end-to-end.
    flip_tb : mirror top<->bottom (swaps the two ports on each side).
    """
    c = gf.Component()
    c.add_ref(AMF_300LSOI_Si2X2MMI_Cband_v5p0())

    # Physical port faces are fixed by the BB geometry; orientation points out.
    WT = dict(center=(0.0,   0.667), orientation=180)   # west top
    WB = dict(center=(0.0,  -0.667), orientation=180)   # west bottom
    ET = dict(center=(75.0,  0.667), orientation=0)     # east top
    EB = dict(center=(75.0, -0.667), orientation=0)     # east bottom

    o1, o2, o3, o4 = WT, WB, ET, EB          # AMF default
    if flip_lr:
        o1, o2, o3, o4 = ET, EB, WT, WB      # inputs on east, outputs on west
    if flip_tb:
        o1, o2, o3, o4 = o2, o1, o4, o3      # swap top/bottom on each side

    for name, face in (("o1", o1), ("o2", o2), ("o3", o3), ("o4", o4)):
        c.add_port(name=name, width=0.5, layer="RIB", **face)
    return c
