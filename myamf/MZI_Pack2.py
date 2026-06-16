import gdsfactory as gf
from .Rib_MZI import Rib_MZI
from .SiN_MZI import SiN_MZI
from .via_MZI import via_MZI
from .strip_MZI import strip_MZI
from .SiN_1250_MZI import SiN_1250_MZI
from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_Si2X2MMI_Cband_v5p0,
    AMF_300LSOI_LSiN2SOISSC_Cband_v5p0,
)

@gf.cell
def MZIs_Pack2()->gf.Component:
    c = gf.Component()

    sin_1250_mzi = c.add_ref(SiN_1250_MZI(gap = 500, dl = 18.375, cross_section = "strip"))
    # sin_mzi.ymin = spiral.ymin
    # sin_mzi.xmin = bpads[48].ports['e1'].center[0]

    sin_mzi = c.add_ref(SiN_MZI(gap = 400, dl = 18.69, cross_section = "strip"))
    sin_mzi.ymax = sin_1250_mzi.ymin - 5
    sin_mzi.xmin = sin_1250_mzi.xmin

    # via_mzi = c.add_ref(via_MZI())
    # via_mzi.ymax = sin_mzi.ymin - 5
    # via_mzi.xmin = sin_mzi.xmin
    #------- I replaced via_mzi with rib, but due to lack of time don't change the namings in this code:
    via_mzi = c.add_ref(Rib_MZI(gap = 180, dl = 9.597, cross_section = "strip", taper_length= 50, strip_width = 0.5))
    via_mzi.ymax = sin_mzi.ymin - 5
    via_mzi.xmin = sin_mzi.xmin

    strip_mzi = c.add_ref(strip_MZI(gap = 100, dl = 9.303, cross_section = "strip"))
    strip_mzi.ymax = via_mzi.ymin - 15
    strip_mzi.xmin = sin_mzi.xmin

    #---------Combiners ------------------

    combiner1 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    combiner1.mirror_x()
    combiner1.xmin = sin_1250_mzi.ports['o2'].center[0] + 30
    combiner1.ymax = sin_1250_mzi.ports['o2'].center[1] - 30

    combiner2 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    combiner2.mirror_x()
    combiner2.xmin = sin_mzi.ports['o2'].center[0] + 30
    combiner2.ymax = sin_mzi.ports['o2'].center[1] - 30

    combiner3 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    combiner3.mirror_x()
    combiner3.xmin = via_mzi.ports['o2'].center[0] + 30
    combiner3.ymax = via_mzi.ports['o2'].center[1] - 30

    combiner4 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    combiner4.mirror_x()
    combiner4.xmin = strip_mzi.ports['o2'].center[0] + 30
    combiner4.ymax = strip_mzi.ports['o2'].center[1] - 30

    #-------------- Vias-----------------------------

    via1 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via1.connect('o1', combiner1.ports['o1'])

    via2 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via2.connect('o1', combiner2.ports['o1'])

    via3 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via3.connect('o1', combiner3.ports['o1'])

    via4 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via4.connect('o1', combiner4.ports['o1'])

    #------------- Splitters--------------------------
    splitter1 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    splitter1.xmax = sin_1250_mzi.xmin - 120
    splitter1.ymin = sin_1250_mzi.ymin - 110

    via0 = c.add_ref(AMF_300LSOI_LSiN2SOISSC_Cband_v5p0())
    via0.mirror_x()
    via0.connect('o1', splitter1.ports['o1'])

    splitter2 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    splitter2.xmin = splitter1.xmax + 30
    splitter2.ymin = splitter1.ymax + 30

    splitter3 = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    splitter3.xmin = splitter1.xmax + 30
    splitter3.ymax = splitter1.ymin - 15

    gf.routing.route_bundle(
        c,
        ports1 = [splitter1.ports['o2'], splitter1.ports['o3']],
        ports2 = [splitter2.ports['o1'], splitter3.ports['o1']],
        cross_section = 'strip',
    )

    gf.routing.route_bundle(
        c,
        ports1 = [splitter2.ports['o2'], splitter2.ports['o3']],
        ports2 = [sin_1250_mzi.ports['o1'], sin_mzi.ports['o1']],
        cross_section = 'strip',
    )
    gf.routing.route_bundle(
        c,
        ports1 = [splitter3.ports['o2'], splitter3.ports['o3']],
        ports2 = [via_mzi.ports['o1'], strip_mzi.ports['o1']],
        cross_section = 'strip',
    )
    

    gf.routing.route_single(
        c,
        port1 = sin_1250_mzi.ports['o2'],
        port2 = combiner1.ports['o2'],
        cross_section = 'strip'
    )
    gf.routing.route_single(
        c,
        port1 = sin_mzi.ports['o2'],
        port2 = combiner2.ports['o2'],
        cross_section = 'strip'
    )
    gf.routing.route_single(
        c,
        port1 = via_mzi.ports['o2'],
        port2 = combiner3.ports['o2'],
        cross_section = 'strip'
    )
    gf.routing.route_single(
        c,
        port1 = strip_mzi.ports['o2'],
        port2 = combiner4.ports['o2'],
        cross_section = 'strip'
    )


    #------- Ports-----------------------------
    c.add_port('o1', port = splitter1.ports['o1'])
    c.add_port('o2', port = combiner1.ports['o3'])
    c.add_port('o3', port = combiner2.ports['o3'])
    c.add_port('o4', port = combiner3.ports['o3'])
    c.add_port('o5', port = combiner4.ports['o3'])

    c.add_port('o6', port = via1.ports['o2'])
    c.add_port('o7', port = via2.ports['o2'])
    c.add_port('o8', port = via3.ports['o2'])
    c.add_port('o9', port = via4.ports['o2'])
    c.add_port('o10', port = via0.ports['o2'])

    return c

